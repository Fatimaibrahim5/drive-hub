"""Number Bonds to 10 - an animated lesson for grade one, taught by a cartoon kid (Omar).

Pipeline: narration script -> Kokoro TTS clips -> timeline -> voice/sfx/music track
-> animated frames drawn with Pillow -> MP4 via ffmpeg.

Requires: pillow, numpy, soundfile, kokoro-onnx (+ kokoro-v1.0.onnx, voices-v1.0.bin),
Fredoka.ttf font, ffmpeg. Paths are set with the env vars below.
"""
import hashlib
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ASSETS = os.environ.get("NB_ASSETS", os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("NB_WORK", os.path.join(ASSETS, "build"))
OUT = os.environ.get("NB_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "number-bonds-to-10.mp4"))
FONT = os.path.join(ASSETS, "Fredoka.ttf")

W, H, S, FPS = 1280, 720, 2, 24
SR = 24000
VOICE = "af_heart"
PITCH = 1.2  # raise pitch so the narrator sounds like a young kid

os.makedirs(WORK, exist_ok=True)

# ---------------------------------------------------------------- script
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
RED, GREEN = "#E63946", "#43AA62"
RAINBOW = ["#E63946", "#F77F00", "#FCBF49", "#43AA62", "#277DA1", "#7B2CBF"]


def cap(s):
    return s[0].upper() + s[1:]


def build_scenes():
    sc = []
    sc.append(dict(kind="intro", title="Hello, friends!", color="#7B2CBF", items=[
        ("say", "hi", "Hi friends! My name is Omar, and I am in grade one, just like you!"),
        ("say", "fun", "Today, I will teach you something super fun."),
        ("say", "title", "Number bonds that make ten!"),
    ]))
    sc.append(dict(kind="what", title="What is a number bond?", color="#277DA1", items=[
        ("say", "fam", "A number bond is like a little family of numbers."),
        ("say", "whole", "The big number on top is the whole. Here, it is ten."),
        ("say", "parts", "The two numbers at the bottom are the parts."),
        ("say", "together", "When we put the two parts together, six and four, we get the whole. Ten!"),
    ]))
    items = [("say", "lets", "Let's count ten apples together!")]
    for i in range(1, 11):
        items.append(("say", f"n{i}", cap(WORDS[i]) + "!"))
    items.append(("say", "yay", "Ten apples! Yay!"))
    sc.append(dict(kind="count", title="Let's count to 10!", color="#F77F00", items=items, gap=0.25))
    for a in (9, 8, 7, 6, 5):
        b = 10 - a
        eq = f"{cap(WORDS[a])} and {WORDS[b]} make ten!"
        if a == 5:
            eq = "Five and five make ten! That is a double!"
        sc.append(dict(kind="bond", a=a, b=b, title=f"Make 10 with {a}", color="#43AA62", items=[
            ("say", "a", f"Look! {cap(WORDS[a])} red apples." if a != 9 else "Look! Nine red apples."),
            ("say", "b", f"And {WORDS[b]} green apple{'s' if b > 1 else ''}."),
            ("say", "eq", eq),
        ]))
    sc.append(dict(kind="switch", title="Switch it around!", color="#E63946", items=[
        ("say", "trick", "Here is a secret trick!"),
        ("say", "switch", "We can switch the parts around."),
        ("say", "e1", "Nine plus one is ten."),
        ("say", "e2", "And one plus nine is ten, too!"),
        ("say", "same", "Same parts, same whole!"),
    ]))
    items = [("say", "lets", "Let's say all the number bonds to ten together!")]
    for i in range(6):
        txt = f"{cap(WORDS[i])} and {WORDS[10 - i]}." if i < 5 else "And five and five!"
        items.append(("say", f"r{i}", txt))
    items.append(("say", "wow", "Wow, look! It makes a rainbow!"))
    sc.append(dict(kind="rainbow", title="The Rainbow of 10", color="#F77F00", items=items))
    items = [("say", "start", "Now it is your turn! Let's play a game.")]
    praise = ["Great job!", "Super!", "You are a superstar!"]
    for k, a in enumerate((7, 4, 2)):
        b = 10 - a
        items += [
            ("say", f"q{k}", f"{cap(WORDS[a])} plus what makes ten?"),
            ("say", f"th{k}", "Think hard!"),
            ("pause", f"p{k}", 3.0),
            ("say", f"ans{k}", f"It is {WORDS[b]}! {cap(WORDS[a])} and {WORDS[b]} make ten! {praise[k]}"),
        ]
    sc.append(dict(kind="quiz", title="Your turn!", color="#7B2CBF", qs=[(7, 3), (4, 6), (2, 8)], items=items))
    sc.append(dict(kind="outro", title="Great job!", color="#E63946", items=[
        ("say", "rem", "Remember, number bonds to ten help us add super fast!"),
        ("say", "bye", "Thanks for learning with me. Bye bye, friends!"),
    ]))
    return sc


# ---------------------------------------------------------------- audio
def tts_clip(text):
    path = os.path.join(WORK, "tts_" + hashlib.md5((VOICE + text).encode()).hexdigest()[:12] + ".wav")
    if not os.path.exists(path):
        from kokoro_onnx import Kokoro
        global _kokoro
        if "_kokoro" not in globals():
            _kokoro = Kokoro(os.path.join(ASSETS, "kokoro-v1.0.onnx"), os.path.join(ASSETS, "voices-v1.0.bin"))
        samples, sr = _kokoro.create(text, voice=VOICE, speed=0.88, lang="en-us")
        assert sr == SR
        sf.write(path, samples, sr)
    data, _ = sf.read(path, dtype="float32")
    # trim leading/trailing near-silence
    idx = np.where(np.abs(data) > 0.01)[0]
    if len(idx):
        data = data[max(0, idx[0] - 240): idx[-1] + 1200]
    return data


def build_timeline(scenes):
    """Assign global start times; returns scenes with ev[tag]=(start,end) in local time, and voice track."""
    t = 0.0
    chunks = []
    for s in scenes:
        s["start"] = t
        local = 0.5
        ev = {}
        gap = s.get("gap", 0.4)
        for kind, tag, val in s["items"]:
            if kind == "say":
                clip = tts_clip(val)
                d = len(clip) / SR
                chunks.append((t + local, clip))
                ev[tag] = (local, local + d, val)
                local += d + gap
            else:
                ev[tag] = (local, local + val, None)
                local += val + 0.2
        local += 0.9
        s["ev"] = ev
        s["dur"] = local
        t += local
    total = t + 0.5
    voice = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for st, clip in chunks:
        i = int(st * SR)
        voice[i:i + len(clip)] += clip
    return scenes, voice, total


def tone(freqs, dur, decay, amp, sweep=None):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        if sweep:
            ph = 2 * np.pi * (f * tt + (sweep - f) * tt * tt / (2 * dur))
        else:
            ph = 2 * np.pi * f * tt
        out += np.sin(ph)
    env = np.exp(-tt / decay) * np.minimum(1, tt / 0.004)
    return (out / len(freqs) * env * amp).astype(np.float32)


SFX = {
    "pop": tone([520], 0.12, 0.035, 0.30, sweep=1250),
    "ding": tone([1046.5, 1568.0], 0.9, 0.25, 0.20),
    "tick": tone([1800], 0.05, 0.012, 0.18),
    "sparkle": np.concatenate([tone([f], 0.09, 0.05, 0.16) for f in (1046.5, 1318.5, 1568.0, 2093.0)]),
}


def pluck(freq, dur=1.2):
    n = int(dur * SR)
    period = int(SR / freq)
    rng = np.random.default_rng(int(freq))
    buf = rng.uniform(-1, 1, period).astype(np.float32)
    out = np.zeros(n, dtype=np.float32)
    for i in range(0, n, period):
        seg = min(period, n - i)
        out[i:i + seg] = buf[:seg]
        buf = 0.5 * (buf + np.roll(buf, -1)) * 0.996
    return out


def music_bed(total):
    """Soft ukulele-style strums on C - G - Am - F at a gentle tempo."""
    chords = [[261.6, 329.6, 392.0], [246.9, 293.7, 392.0], [261.6, 329.6, 440.0], [261.6, 349.2, 440.0]]
    cache = {}
    beat = 60 / 92
    out = np.zeros(int(total * SR) + SR * 2, dtype=np.float32)
    b = 0
    while b * beat < total:
        ch = chords[(b // 4) % 4]
        for k, f in enumerate(ch):
            if f not in cache:
                cache[f] = pluck(f)
            i = int((b * beat + k * 0.018) * SR)
            p = cache[f] * (1.0 if b % 2 == 0 else 0.6)
            out[i:i + len(p)] += p[: len(out) - i]
        b += 1
    return out * 0.035


# ---------------------------------------------------------------- drawing helpers
_fonts = {}


def font(size, weight=600):
    key = (size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(FONT, int(size * S))
        f.set_variation_by_axes([weight, 100])
        _fonts[key] = f
    return _fonts[key]


def P(*v):
    return [x * S for x in v]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_back(p):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def pop(t, t0, dur=0.35):
    if t0 is None or t < t0:
        return 0.0
    return ease_back(clamp((t - t0) / dur))


def text(d, xy, s, size, fill, weight=600, anchor="mm", stroke=0, stroke_fill="white", scale=1.0):
    if scale <= 0.02:
        return
    d.text(P(*xy), s, font=font(max(1, size * scale), weight), fill=fill, anchor=anchor,
           stroke_width=int(stroke * S * scale), stroke_fill=stroke_fill)


def circle(d, cx, cy, r, fill=None, outline=None, width=0):
    if r <= 0:
        return
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=int(width * S))


def lighten(hexc, k):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return tuple(int(v + (255 - v) * k) for v in c)


def star(d, cx, cy, r, fill, rot=0.0):
    pts = []
    for i in range(10):
        a = rot + i * math.pi / 5 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts += [cx + rr * math.cos(a), cy + rr * math.sin(a)]
    d.polygon(P(*pts), fill=fill)


def apple(d, cx, cy, r, color, scale=1.0):
    r *= scale
    if r <= 1:
        return
    leaf = "#2D6A4F"
    d.line(P(cx, cy - r * 0.7, cx + r * 0.18, cy - r * 1.25), fill="#6B4226", width=max(1, int(r * 0.16 * S)))
    d.ellipse(P(cx + r * 0.1, cy - r * 1.25, cx + r * 0.75, cy - r * 0.95), fill=leaf)
    d.ellipse(P(cx - r, cy - r * 0.85, cx + r * 0.15, cy + r), fill=color)
    d.ellipse(P(cx - r * 0.15, cy - r * 0.85, cx + r, cy + r), fill=color)
    d.ellipse(P(cx - r * 0.62, cy - r * 0.5, cx - r * 0.3, cy - r * 0.02), fill=lighten(color, 0.55))


def ten_frame(d, x0, y0, c):
    d.rounded_rectangle(P(x0 - 8, y0 - 8, x0 + 5 * c + 8, y0 + 2 * c + 8), radius=14 * S, fill="#264653")
    for i in range(10):
        cx, cy = x0 + (i % 5) * c, y0 + (i // 5) * c
        d.rounded_rectangle(P(cx + 4, cy + 4, cx + c - 4, cy + c - 4), radius=8 * S, fill="#FFF8E7")


def cell_center(x0, y0, c, i):
    return x0 + (i % 5) * c + c / 2, y0 + (i // 5) * c + c / 2 + c * 0.04


def bond(d, cx, cy, whole, a, b, k=1.0, sc=(1, 1, 1), labels=False, pulse=(0, 0, 0), qmark=None, t=0.0):
    """Number-bond diagram. sc = pop scales of whole/part a/part b circles."""
    R, r, dx, dy = 58 * k, 48 * k, 100 * k, 150 * k
    wx, wy = cx, cy - dy / 2
    ax, ay, bx, by = cx - dx, cy + dy / 2, cx + dx, cy + dy / 2
    lw = 8 * k
    if sc[1] > 0.3:
        d.line(P(wx, wy, ax, ay), fill="#264653", width=int(lw * S))
    if sc[2] > 0.3:
        d.line(P(wx, wy, bx, by), fill="#264653", width=int(lw * S))
    specs = [(wx, wy, R, "#FFD166", "#E09F00", whole, "WHOLE"),
             (ax, ay, r, "#FFC2C7", RED, a, "PART"),
             (bx, by, r, "#C7EFCF", GREEN, b, "PART")]
    for j, (x, y, rr, fill, edge, val, lab) in enumerate(specs):
        s = sc[j]
        if s <= 0:
            continue
        pu = 1 + 0.08 * pulse[j] * math.sin(t * 9)
        circle(d, x, y, rr * s * pu, fill=fill, outline=edge, width=7 * k * s)
        if val is not None:
            col = "#264653" if val != "?" else "#7B2CBF"
            vs = s * (1 + (0.12 * math.sin(t * 8) if val == "?" else 0))
            text(d, (x, y + 2 * k), str(val), 52 * k * (0.9 if j else 1), col, 700, scale=vs)
        if labels:
            if j == 0:
                text(d, (x + rr + 14 * k, y), lab, 22 * k, edge, 700, anchor="lm", scale=s)
            else:
                text(d, (x, y + rr + 24 * k), lab, 22 * k, edge, 700, scale=s)


def equation(d, cx, cy, parts, size, scale=1.0, stroke=6):
    if scale <= 0.02:
        return
    f = font(size * scale, 700)
    gap = 14 * scale
    widths = [f.getlength(s) / S for s, _ in parts]
    total = sum(widths) + gap * (len(parts) - 1)
    x = cx - total / 2
    for (s, col), w in zip(parts, widths):
        d.text(P(x, cy), s, font=f, fill=col, anchor="lm", stroke_width=int(stroke * S * scale), stroke_fill="white")
        x += w + gap


def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) / S > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- background + kid
BOARD = (360, 104, 1258, 606)
CAPBOX = (360, 620, 1258, 706)
_bg = None


def background():
    global _bg
    if _bg is None:
        img = Image.new("RGB", (W * S, H * S))
        d = ImageDraw.Draw(img)
        for y in range(H * S):
            k = y / (H * S)
            d.line([(0, y), (W * S, y)], fill=(int(120 + 90 * k), int(200 + 40 * k), 255))
        for (x, y, s) in [(120, 80, 1.0), (300, 40, 0.7), (1150, 55, 0.6)]:
            for ox, oy, r in [(-40, 10, 30), (0, 0, 40), (40, 10, 30), (0, 18, 32)]:
                circle(d, x + ox * s, y + oy * s, r * s, fill="white")
        d.ellipse(P(-200, 600, 700, 900), fill="#7ED957")
        d.ellipse(P(500, 640, 1500, 950), fill="#6CC644")
        for x in range(10, 340, 28):
            d.polygon(P(x, 700, x + 6, 684, x + 12, 700), fill="#57B33A")
        bx0, by0, bx1, by1 = BOARD
        d.rounded_rectangle(P(bx0 + 6, by0 + 8, bx1 + 6, by1 + 8), radius=34 * S, fill=(70, 120, 160))
        d.rounded_rectangle(P(*BOARD), radius=34 * S, fill="#FFFDF5", outline="#FFB703", width=10 * S)
        d.rounded_rectangle(P(*CAPBOX), radius=24 * S, fill="#FFFFFF", outline="#C9B6F2", width=4 * S)
        _bg = img
    return _bg.copy()


def draw_sun(d, t):
    cx, cy = 48, 48
    for i in range(10):
        a = t * 0.6 + i * math.pi / 5
        d.line(P(cx + 44 * math.cos(a), cy + 44 * math.sin(a), cx + 64 * math.cos(a), cy + 64 * math.sin(a)),
               fill="#FFC300", width=7 * S)
    circle(d, cx, cy, 36, fill="#FFD60A")
    circle(d, cx - 12, cy - 4, 4, fill="#7A4E00")
    circle(d, cx + 12, cy - 4, 4, fill="#7A4E00")
    d.arc(P(cx - 14, cy - 6, cx + 14, cy + 16), 20, 160, fill="#7A4E00", width=3 * S)


SKIN, SKIN_D, HAIR, SHIRT = "#E8B58A", "#C98E62", "#3B2314", "#2EC4B6"


def limb(d, pts, sleeve_frac=0.42):
    (x0, y0), (x1, y1), (x2, y2) = pts
    d.line(P(x0, y0, x1, y1, x2, y2), fill=SKIN, width=22 * S, joint="curve")
    sx, sy = x0 + (x1 - x0) * sleeve_frac * 2, y0 + (y1 - y0) * sleeve_frac * 2
    d.line(P(x0, y0, sx, sy), fill=SHIRT, width=30 * S)
    circle(d, x0, y0, 15, fill=SHIRT)
    circle(d, x2, y2, 15, fill=SKIN)


def draw_kid(d, t, mouth, pose):
    cx = 185
    bob = -4 * mouth + 2 * math.sin(t * 2.2)
    # legs + shoes
    d.rounded_rectangle(P(150, 560, 182, 668), radius=10 * S, fill="#2B4C8C")
    d.rounded_rectangle(P(188, 560, 220, 668), radius=10 * S, fill="#2B4C8C")
    d.ellipse(P(136, 652, 186, 682), fill="#E63946")
    d.ellipse(P(184, 652, 236, 682), fill="#E63946")
    # body
    d.rounded_rectangle(P(116, 430 + bob * 0.4, 254, 590), radius=44 * S, fill=SHIRT)
    star(d, cx, 512 + bob * 0.4, 30, "#FFD166", rot=0.0)
    text(d, (cx, 515 + bob * 0.4), "10", 22, "#E63946", 700)
    # arms
    if pose in ("wave", "bye"):
        sw = math.sin(t * 9) * 16
        limb(d, [(128, 458), (86, 410), (78 + sw, 336)])
    else:
        limb(d, [(128, 458), (106, 520), (112, 578)])
    if pose == "point":
        wob = math.sin(t * 3) * 6
        limb(d, [(242, 458), (282, 430), (330, 392 + wob)])
    elif pose == "think":
        limb(d, [(242, 458), (262, 500), (214, 420)])
    else:
        limb(d, [(242, 458), (264, 520), (258, 578)])
    # neck + head
    d.rectangle(P(172, 400 + bob, 198, 440 + bob), fill=SKIN_D)
    hy = 330 + bob
    circle(d, 97, hy + 8, 16, fill=SKIN_D)
    circle(d, 273, hy + 8, 16, fill=SKIN_D)
    d.ellipse(P(93, hy - 100, 277, hy + 40), fill=HAIR)
    for i in range(5):
        x = 112 + i * 34
        d.polygon(P(x, hy - 78, x + 22, hy - 118 + (i % 2) * 10, x + 40, hy - 74), fill=HAIR)
    d.ellipse(P(103, hy - 72, 267, hy + 90), fill=SKIN)
    d.chord(P(103, hy - 110, 267, hy - 6), 180, 360, fill=HAIR)
    d.polygon(P(160, hy - 60, 205, hy - 60, 228, hy - 34, 180, hy - 48), fill=HAIR)
    # eyes
    blink = (t % 3.7) < 0.13
    look = 4 if pose in ("point", "think") else 0
    for ex in (152, 218):
        ey = hy + 4
        if blink:
            d.arc(P(ex - 15, ey - 8, ex + 15, ey + 10), 20, 160, fill="#2B1B10", width=4 * S)
        else:
            d.ellipse(P(ex - 15, ey - 19, ex + 15, ey + 19), fill="white")
            circle(d, ex + look, ey + 2, 9.5, fill="#2B1B10")
            circle(d, ex + look + 3, ey - 2, 3.5, fill="white")
        brow = hy - 28 - 4 * mouth
        d.arc(P(ex - 16, brow, ex + 16, brow + 14), 200, 340, fill=HAIR, width=5 * S)
    # cheeks + nose
    d.ellipse(P(118, hy + 30, 146, hy + 46), fill="#F7A1A1")
    d.ellipse(P(224, hy + 30, 252, hy + 46), fill="#F7A1A1")
    d.arc(P(176, hy + 16, 194, hy + 32), 20, 160, fill=SKIN_D, width=4 * S)
    # mouth
    my = hy + 52
    if mouth < 0.08:
        d.arc(P(160, my - 22, 210, my + 8), 25, 155, fill="#8B1E3F", width=5 * S)
    else:
        h = 6 + 26 * mouth
        w = 22 - 3 * mouth
        d.chord(P(cx - w, my - h * 0.35, cx + w, my + h), 0, 180, fill="#8B1E3F")
        d.rectangle(P(cx - w + 6, my - h * 0.35 + 0, cx + w - 6, my + 2), fill="#8B1E3F")
        d.rectangle(P(cx - w + 7, my - 1, cx + w - 7, my + 4), fill="white")
        if h > 14:
            d.ellipse(P(cx - 10, my + h * 0.45, cx + 10, my + h * 0.95), fill="#F28B9B")


# ---------------------------------------------------------------- scene drawing
BX = (BOARD[0] + BOARD[2]) / 2  # board centre x (809)


def ev_t(ev, tag, which=0):
    return ev[tag][which] if tag in ev else None


def scene_intro(d, s, t):
    ev = s["ev"]
    p = pop(t, ev_t(ev, "hi"))
    text(d, (BX, 220), "Hi! I'm Omar", 78, "#7B2CBF", 700, stroke=8, scale=p)
    p2 = pop(t, ev_t(ev, "fun"))
    for i, col in enumerate(RAINBOW):
        x = 470 + i * 136
        star(d, x, 330 + 10 * math.sin(t * 3 + i), 30 * p2, col, rot=t * 0.8 + i)
    title = "Number Bonds"
    t0 = ev_t(ev, "title")
    if t0 is not None:
        f = font(84, 700)
        total = f.getlength(title) / S
        x = BX - total / 2
        for i, ch in enumerate(title):
            w = f.getlength(ch) / S
            pp = pop(t, t0 + i * 0.05)
            if ch != " ":
                text(d, (x + w / 2, 440), ch, 84, RAINBOW[i % 6], 700, stroke=8, scale=pp)
            x += w
        pp = pop(t, t0 + 0.9, 0.5)
        text(d, (BX, 535), "to 10", 72, "#264653", 700, stroke=8, scale=pp)


def scene_what(d, s, t):
    ev = s["ev"]
    ps = pop(t, ev_t(ev, "fam"))
    tw = ev_t(ev, "whole")
    tp = ev_t(ev, "parts")
    tt = ev_t(ev, "together")
    whole = "10" if tw is not None and t >= tw else None
    pa = "6" if tp is not None and t >= tp else None
    pb = "4" if tp is not None and t >= tp + 0.3 else None
    pulse = (1 if tw is not None and tw <= t < tp else 0, 1 if tp <= t < tt else 0, 1 if tp <= t < tt else 0)
    bond(d, BX, 282, whole, pa, pb, k=1.25, sc=(ps, ps, ps), labels=t >= tw, pulse=pulse, t=t)
    if t >= tt:
        p = pop(t, tt + 1.0)
        equation(d, BX, 540, [("6", RED), ("+", "#264653"), ("4", GREEN), ("=", "#264653"), ("10", "#E09F00")], 66, p)


def scene_count(d, s, t):
    ev = s["ev"]
    c, x0, y0 = 92, BX - 230, 175
    ten_frame(d, x0, y0, c)
    last = 0
    for i in range(1, 11):
        t0 = ev_t(ev, f"n{i}")
        p = pop(t, t0)
        if p > 0:
            cx, cy = cell_center(x0, y0, c, i - 1)
            apple(d, cx, cy, 30, RED if i <= 5 else "#F77F00", p)
            last = i
    if last:
        t0 = ev_t(ev, f"n{last}")
        text(d, (BX, 500), str(last), 120, RAINBOW[last % 6], 700, stroke=10, scale=pop(t, t0))
    ty = ev_t(ev, "yay")
    if ty is not None and t >= ty:
        for i in range(8):
            a = i * math.pi / 4 + t
            rr = 160 + 20 * math.sin(t * 4)
            star(d, BX + rr * 1.6 * math.cos(a), 500 + rr * 0.5 * math.sin(a), 18 * pop(t, ty), RAINBOW[i % 6], rot=t)


def apples_staggered(d, t, t0, x0, y0, c, start, count, color, step=0.14, r=27):
    if t0 is None:
        return
    for j in range(count):
        p = pop(t, t0 + j * step)
        if p > 0:
            cx, cy = cell_center(x0, y0, c, start + j)
            apple(d, cx, cy, r, color, p)


def scene_bond(d, s, t):
    ev = s["ev"]
    a, b = s["a"], s["b"]
    c, x0, y0 = 76, 420, 175
    ten_frame(d, x0, y0, c)
    ta, tb, te = ev_t(ev, "a"), ev_t(ev, "b"), ev_t(ev, "eq")
    apples_staggered(d, t, ta, x0, y0, c, 0, a, RED)
    apples_staggered(d, t, tb, x0, y0, c, a, b, GREEN)
    ps = pop(t, 0.1)
    bond(d, 1075, 255, "10" if t >= te else None, str(a) if t >= ta else None, str(b) if t >= tb else None,
         k=0.95, sc=(ps, ps, ps), pulse=(1 if t >= te else 0, 0, 0), t=t)
    if t >= ta:
        text(d, (x0 + 5 * c / 2 - 85, 378), f"{a} red", 34, RED, 700, scale=pop(t, ta))
    if t >= tb:
        text(d, (x0 + 5 * c / 2 + 85, 378), f"{b} green", 34, GREEN, 700, scale=pop(t, tb))
    p = pop(t, te)
    equation(d, BX, 500, [(str(a), RED), ("+", "#264653"), (str(b), GREEN), ("=", "#264653"), ("10", "#E09F00")], 92, p)
    if a == 5 and t >= te + 1.2:
        text(d, (BX, 570), "A double!", 34, "#7B2CBF", 700, scale=pop(t, te + 1.2))


def curved_arrow(d, x0, x1, y, h, p, col):
    if p <= 0:
        return
    n = 24
    pts = []
    for i in range(int(n * p) + 1):
        u = i / n
        pts += [x0 + (x1 - x0) * u, y - h * math.sin(math.pi * u)]
    if len(pts) >= 4:
        d.line(P(*pts), fill=col, width=8 * S, joint="curve")
        ex, ey = pts[-2], pts[-1]
        circle(d, ex, ey, 10, fill=col)


def scene_switch(d, s, t):
    ev = s["ev"]
    p1 = pop(t, ev_t(ev, "trick"))
    p2 = pop(t, ev_t(ev, "switch"))
    same = ev_t(ev, "same")
    pu = 1 if t >= same else 0
    bond(d, 590, 280, "10", "9", "1", k=0.85, sc=(p1, p1, p1), pulse=(pu, 0, 0), t=t)
    # right diagram swaps colours: draw manually-coloured parts by swapping values
    bond(d, 1030, 280, "10", "1", "9", k=0.85, sc=(p2, p2, p2), pulse=(pu, 0, 0), t=t)
    ts = ev_t(ev, "switch")
    if t >= ts:
        pa = clamp((t - ts) / 1.0)
        curved_arrow(d, 690, 930, 200, 70, pa, "#F77F00")
        text(d, (810, 215), "switch!", 30, "#F77F00", 700, scale=pop(t, ts + 0.8))
    equation(d, 590, 470, [("9", RED), ("+", "#264653"), ("1", GREEN), ("=", "#264653"), ("10", "#E09F00")], 64,
             pop(t, ev_t(ev, "e1")))
    equation(d, 1030, 470, [("1", RED), ("+", "#264653"), ("9", GREEN), ("=", "#264653"), ("10", "#E09F00")], 64,
             pop(t, ev_t(ev, "e2")))
    if t >= same:
        text(d, (BX, 560), "Same parts, same whole!", 40, "#7B2CBF", 700, stroke=4, scale=pop(t, same))
        for i in range(6):
            star(d, 420 + i * 155, 140 + 8 * math.sin(t * 5 + i), 14 * pop(t, same + i * 0.08), RAINBOW[i], rot=t)


def scene_rainbow(d, s, t):
    ev = s["ev"]
    xs = [430 + i * 76 for i in range(11)]
    base = 505
    tw = ev_t(ev, "wow")
    cur = None
    for i in range(6):
        t0 = ev_t(ev, f"r{i}")
        if t0 is None or t < t0:
            continue
        cur = i
        p = clamp((t - t0) / 0.8)
        col = RAINBOW[i]
        wpx = 12 + (3 * math.sin(t * 6) if tw is not None and t >= tw else 0)
        if i < 5:
            x0, x1 = xs[i], xs[10 - i]
            hw = (x1 - x0) / 2
            hh = hw * 0.82
            d.arc(P(x0, base - hh - 30, x1, base + hh - 30), 180, 180 + 180 * p, fill=col, width=int(wpx * S))
        else:
            d.arc(P(xs[5] - 26, base - 92, xs[5] + 26, base - 40), 90, 90 + 360 * p, fill=col, width=int(wpx * S))
    for i, x in enumerate(xs):
        k = min(i, 10 - i)
        lit = cur is not None and k <= cur
        fill = lighten(RAINBOW[k], 0.75) if lit else "#EEEEEE"
        edge = RAINBOW[k] if lit else "#BBBBBB"
        circle(d, x, base, 28, fill=fill, outline=edge, width=5)
        text(d, (x, base + 2), str(i), 34, "#264653", 700)
    if cur is not None and (tw is None or t < tw):
        a, b = cur, 10 - cur
        equation(d, BX, 576, [(str(a), RAINBOW[cur]), ("+", "#264653"), (str(b), RAINBOW[cur]), ("=", "#264653"),
                              ("10", "#264653")], 40, pop(t, ev_t(ev, f"r{cur}"), 0.25), stroke=3)
    if tw is not None and t >= tw:
        text(d, (BX, 576), "A rainbow of 10!", 40, "#7B2CBF", 700, stroke=3, scale=pop(t, tw))
        for i in range(6):
            a = math.pi + i * math.pi / 5
            star(d, BX + 420 * math.cos(a), 470 + 330 * math.sin(a) * 0.95, 16 * pop(t, tw + i * 0.07),
                 RAINBOW[i], rot=t)


def quiz_state(s, t):
    ev = s["ev"]
    k = None
    for j in range(3):
        if t >= ev[f"q{j}"][0]:
            k = j
    return k


def scene_quiz(d, s, t):
    ev = s["ev"]
    k = quiz_state(s, t)
    if k is None:
        p = pop(t, ev_t(ev, "start"))
        text(d, (BX, 300), "Let's play!", 96, "#7B2CBF", 700, stroke=8, scale=p)
        for i in range(6):
            star(d, 470 + i * 136, 440 + 10 * math.sin(t * 4 + i), 28 * p, RAINBOW[i], rot=t + i)
        return
    a, b = s["qs"][k]
    tq, tth = ev[f"q{k}"][0], ev[f"th{k}"][0]
    pst, pen = ev[f"p{k}"][0], ev[f"p{k}"][1]
    tans = ev[f"ans{k}"][0]
    c, x0, y0 = 76, 420, 175
    ten_frame(d, x0, y0, c)
    apples_staggered(d, t, tq, x0, y0, c, 0, a, RED, step=0.08)
    revealed = t >= tans
    if revealed:
        apples_staggered(d, t, tans, x0, y0, c, a, b, GREEN, step=0.12)
    else:
        for j in range(a, 10):
            cx, cy = cell_center(x0, y0, c, j)
            text(d, (cx, cy), "?", 40, lighten("#7B2CBF", 0.45), 700, scale=1 + 0.1 * math.sin(t * 6 + j))
    ps = pop(t, tq)
    bond(d, 1075, 255, "10", str(a), str(b) if revealed else "?", k=0.95, sc=(ps, ps, ps),
         pulse=(0, 0, 0 if revealed else 1), t=t)
    if revealed:
        equation(d, BX, 500, [(str(a), RED), ("+", "#264653"), (str(b), GREEN), ("=", "#264653"), ("10", "#E09F00")],
                 92, pop(t, tans))
        for i in range(5):
            star(d, 520 + i * 145, 572 + 6 * math.sin(t * 6 + i), 16 * pop(t, tans + 0.3 + i * 0.1),
                 RAINBOW[i], rot=t)
    else:
        equation(d, BX, 500, [(str(a), RED), ("+", "#264653"), ("?", "#7B2CBF"), ("=", "#264653"), ("10", "#E09F00")],
                 92, pop(t, tq))
        if pst <= t < pen:
            n = 3 - int(t - pst)
            frac = (t - pst) % 1
            circle(d, 1180, 520, 44, fill="#FFF1C1", outline="#F77F00", width=6)
            d.arc(P(1136, 476, 1224, 564), -90, -90 + 360 * frac, fill="#F77F00", width=8 * S)
            text(d, (1180, 522), str(n), 50, "#F77F00", 700, scale=1.15 - 0.15 * frac)


def scene_outro(d, s, t):
    ev = s["ev"]
    tr, tb = ev_t(ev, "rem"), ev_t(ev, "bye")
    for i in range(6):
        a = 10 - i
        col = RAINBOW[i]
        cx = 520 + (i % 3) * 290
        cy = 190 + (i // 3) * 120
        p = pop(t, tr + i * 0.25)
        if p <= 0:
            continue
        w, h = 120 * p, 46 * p
        d.rounded_rectangle(P(cx - w, cy - h, cx + w, cy + h), radius=int(22 * S * p), fill=lighten(col, 0.8),
                            outline=col, width=int(6 * S))
        text(d, (cx, cy + 2), f"{a} + {i} = 10", 40, col, 700, scale=p)
    if tb is not None and t >= tb:
        p = pop(t, tb, 0.5)
        text(d, (BX, 490), "Bye bye!", 100, "#E63946", 700, stroke=10, scale=p)
        for i in range(10):
            a = i * math.pi / 5 + t * 0.7
            star(d, BX + 330 * math.cos(a), 490 + 80 * math.sin(a), 16 * p, RAINBOW[i % 6], rot=t)


SCENE_FN = dict(intro=scene_intro, what=scene_what, count=scene_count, bond=scene_bond, switch=scene_switch,
                rainbow=scene_rainbow, quiz=scene_quiz, outro=scene_outro)


def kid_pose(s, t):
    ev = s["ev"]
    if s["kind"] == "intro":
        return "wave"
    if s["kind"] == "outro":
        return "bye" if t >= ev["bye"][0] else "point"
    if s["kind"] == "quiz":
        for j in range(3):
            if ev[f"th{j}"][0] <= t < ev[f"p{j}"][1]:
                return "think"
    return "point"


def caption_for(s, t):
    for tag, (a, b, txt) in s["ev"].items():
        if txt and a - 0.05 <= t <= b + 0.25:
            return txt
    for tag, (a, b, txt) in s["ev"].items():
        if txt is None and a <= t <= b:
            return "Think... think... think..."
    return None


# ---------------------------------------------------------------- render
G = {}


def render_frame(fi):
    scenes, mouth = G["scenes"], G["mouth"]
    T = fi / FPS
    s = scenes[-1]
    for sc in scenes:
        if sc["start"] <= T < sc["start"] + sc["dur"]:
            s = sc
            break
    t = T - s["start"]
    img = background()
    d = ImageDraw.Draw(img)
    draw_sun(d, T)
    # title banner
    pt = pop(t, 0.0, 0.45)
    if pt > 0:
        f = font(40, 700)
        tw = f.getlength(s["title"]) / S + 70
        cx, cy = BX, 52
        d.rounded_rectangle(P(cx - tw / 2 * pt, cy - 34 * pt, cx + tw / 2 * pt, cy + 34 * pt),
                            radius=int(30 * S * pt), fill=s["color"], outline="white", width=int(5 * S))
        text(d, (cx, cy + 2), s["title"], 40, "white", 700, scale=pt)
    SCENE_FN[s["kind"]](d, s, t)
    m = float(mouth[min(fi, len(mouth) - 1)])
    draw_kid(d, T, m, kid_pose(s, t))
    capt = caption_for(s, t)
    if capt:
        f = font(32, 600)
        lines = wrap(capt, f, CAPBOX[2] - CAPBOX[0] - 40)
        cy = (CAPBOX[1] + CAPBOX[3]) / 2
        size = 32 if len(lines) == 1 else 27
        for li, ln in enumerate(lines[:2]):
            off = 0 if len(lines) == 1 else (li - 0.5) * 34
            text(d, (BX, cy + off), ln, size, "#3C2A78", 600)
    return img.reduce(S).tobytes()


def render_chunk(args):
    lo, hi, path = args
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path],
        stdin=subprocess.PIPE)
    for fi in range(lo, hi):
        proc.stdin.write(render_frame(fi))
    proc.stdin.close()
    proc.wait()
    return path


def init_worker(scenes, mouth):
    G["scenes"], G["mouth"] = scenes, mouth


def main():
    scenes, voice, total = build_timeline(build_scenes())
    print(f"total duration {total:.1f}s")
    # pitch-shift the voice (keeps timing) so it sounds like a child
    vin, vout = os.path.join(WORK, "voice_raw.wav"), os.path.join(WORK, "voice_kid.wav")
    sf.write(vin, voice, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vin, "-af",
                    f"asetrate={SR * PITCH:.0f},aresample={SR},atempo={1 / PITCH:.6f}", vout], check=True)
    kid, _ = sf.read(vout, dtype="float32")
    n = len(voice)
    kid = np.pad(kid, (0, max(0, n - len(kid))))[:n]
    mix = kid * 0.95 + music_bed(total)[:n]

    def add(name, at):
        i = int(at * SR)
        clip = SFX[name][: max(0, n - i)]
        mix[i:i + len(clip)] += clip

    for s in scenes:
        st, ev = s["start"], s["ev"]
        add("pop", st + 0.05)
        k = s["kind"]
        if k == "count":
            for i in range(1, 11):
                add("pop", st + ev[f"n{i}"][0])
            add("sparkle", st + ev["yay"][0])
        elif k in ("bond", "quiz"):
            groups = [("a", s.get("a", 0), 0.14), ("b", s.get("b", 0), 0.14)] if k == "bond" else []
            for tag, cnt, step in groups:
                for j in range(cnt):
                    add("pop", st + ev[tag][0] + j * step)
            if k == "bond":
                add("ding", st + ev["eq"][0])
            else:
                for j, (a, b) in enumerate(s["qs"]):
                    for q in range(a):
                        add("pop", st + ev[f"q{j}"][0] + q * 0.08)
                    p0 = ev[f"p{j}"][0]
                    for sec in range(3):
                        add("tick", st + p0 + sec)
                    for q in range(b):
                        add("pop", st + ev[f"ans{j}"][0] + q * 0.12)
                    add("sparkle", st + ev[f"ans{j}"][0] + 0.4)
        elif k == "what":
            add("ding", st + ev["together"][0] + 1.0)
        elif k == "switch":
            add("ding", st + ev["e1"][0])
            add("ding", st + ev["e2"][0])
            add("sparkle", st + ev["same"][0])
        elif k == "rainbow":
            for i in range(6):
                add("pop", st + ev[f"r{i}"][0])
            add("sparkle", st + ev["wow"][0])
        elif k == "intro":
            add("sparkle", st + ev["title"][0])
        elif k == "outro":
            add("sparkle", st + ev["bye"][0])
    mix /= max(1.0, float(np.abs(mix).max()) / 0.95)
    apath = os.path.join(WORK, "mix.wav")
    sf.write(apath, mix, SR)

    # mouth envelope from the voice track
    nframes = int(total * FPS)
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nframes)])
    ref = np.percentile(rms[rms > 0.005], 90) if np.any(rms > 0.005) else 1.0
    mouth = np.clip((rms - 0.006) / ref, 0, 1)
    # small wobble so the mouth opens/closes like syllables instead of a static open shape
    wob = 0.65 + 0.35 * np.abs(np.sin(np.arange(nframes) * 1.7))
    mouth = np.where(mouth > 0.05, mouth * wob, 0)

    nproc = int(os.environ.get("NB_PROCS", os.cpu_count() or 2))
    limit = int(os.environ.get("NB_FRAMES", nframes))
    bounds = np.linspace(0, min(limit, nframes), nproc * 2 + 1).astype(int)
    jobs = [(int(bounds[i]), int(bounds[i + 1]), os.path.join(WORK, f"seg{i:02d}.mp4")) for i in range(len(bounds) - 1)]
    with Pool(nproc, initializer=init_worker, initargs=(scenes, mouth)) as pool:
        segs = pool.map(render_chunk, jobs)
    lst = os.path.join(WORK, "segs.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in segs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", apath,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", OUT], check=True)
    print("wrote", OUT)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        # render preview stills at given global times: python make_video.py still 3.0 12.5 ...
        scenes, voice, total = build_timeline(build_scenes())
        init_worker(scenes, np.full(int(total * FPS) + 1, 0.6))
        for ts in sys.argv[2:]:
            fi = int(float(ts) * FPS)
            Image.frombytes("RGB", (W, H), render_frame(fi)).save(os.path.join(WORK, f"still_{ts}.png"))
        print([(s["kind"], round(s["start"], 1), round(s["dur"], 1)) for s in scenes])
    else:
        main()
