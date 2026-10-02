document.addEventListener("DOMContentLoaded", function () {
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Hero video pause / play ---------- */
  var video = document.querySelector(".hero-video");
  var vBtn = document.querySelector(".video-toggle");
  if (video) {
    var p = video.play();
    if (p && p.catch) p.catch(function () {});
  }
  if (video && vBtn) {
    vBtn.addEventListener("click", function () {
      if (video.paused) {
        video.play();
        vBtn.textContent = "Pause video";
      } else {
        video.pause();
        vBtn.textContent = "Play video";
      }
    });
  }

  /* ---------- Featured cars ---------- */
  var grid = document.getElementById("featured-grid");
  if (!grid) return;

  grid.innerHTML = CARS.map(function (c, i) {
    return (
      '<article class="car-card reveal d' + i + '">' +
        '<div class="flip" tabindex="0" aria-label="' + c.brand + ' ' + c.model + ' - front and rear view">' +
          '<div class="flip-inner">' +
            '<div class="face front"><img src="' + c.front + '" alt="' + c.brand + ' ' + c.model + ' front view"><span class="tag">Front</span></div>' +
            '<div class="face back"><img src="' + c.back + '" alt="' + c.brand + ' ' + c.model + ' rear view"><span class="tag">Rear</span></div>' +
          '</div>' +
          '<div class="flip-dots">' +
            '<button type="button" data-side="front" class="on">Front</button>' +
            '<button type="button" data-side="back">Rear</button>' +
          '</div>' +
        '</div>' +
        '<div class="car-info">' +
          '<p class="brand">' + c.brand + '</p>' +
          '<h3>' + c.model + '</h3>' +
          '<ul class="meta">' +
            '<li><span>Price</span><strong>' + formatPrice(c.price) + '</strong></li>' +
            '<li><span>Mileage</span><strong>' + formatMiles(c.mileage) + '</strong></li>' +
          '</ul>' +
          '<a class="btn btn-light" href="inventory.html#' + c.id + '">View Details</a>' +
        '</div>' +
      '</article>'
    );
  }).join("");

  observeReveals();

  grid.querySelectorAll(".flip").forEach(function (flip, i) {
    var isBack = false;
    var timer = null;
    var dots = flip.querySelectorAll(".flip-dots button");

    function show(back) {
      isBack = back;
      flip.classList.toggle("is-back", back);
      dots[0].classList.toggle("on", !back);
      dots[1].classList.toggle("on", back);
    }
    function stop() { clearInterval(timer); timer = null; }
    function start() {
      if (reduceMotion || timer) return;
      timer = setInterval(function () { show(!isBack); }, 3800);
    }

    flip.addEventListener("mouseenter", stop);
    flip.addEventListener("mouseleave", start);
    flip.addEventListener("focusin", stop);
    flip.addEventListener("focusout", start);
    flip.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      show(btn ? btn.dataset.side === "back" : !isBack);
    });
    flip.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        show(!isBack);
      }
    });

    // Start when the card scrolls into view: front first, then it swings to the rear.
    var begin = function () {
      setTimeout(function () {
        show(true);
        start();
      }, 1400 + i * 600);
    };
    if ("IntersectionObserver" in window && !reduceMotion) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          io.disconnect();
          begin();
        }
      }, { threshold: 0.5 });
      io.observe(flip);
    }
  });
});
