document.addEventListener("DOMContentLoaded", function () {
  var carSel = document.getElementById("car");
  var price = document.getElementById("price");
  var down = document.getElementById("down");
  var downRange = document.getElementById("down-range");
  var downHint = document.getElementById("down-hint");
  var term = document.getElementById("term");
  var rate = document.getElementById("rate");
  var err = document.getElementById("calc-error");
  var applyLink = document.getElementById("apply-link");

  carSel.innerHTML =
    '<option value="custom">Custom price</option>' +
    CARS.map(function (c) {
      return '<option value="' + c.id + '">' + c.brand + " " + c.model + " - " + formatPrice(c.price) + "</option>";
    }).join("");

  var preset = new URLSearchParams(location.search).get("car");
  if (preset && getCar(preset)) {
    carSel.value = preset;
    price.value = getCar(preset).price;
    down.value = Math.round(getCar(preset).price * 0.2);
  }

  var money = function (n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  };

  function num(el) {
    var v = parseFloat(el.value);
    return isNaN(v) || v < 0 ? 0 : v;
  }

  function calculate() {
    var p = num(price);
    var d = num(down);
    var months = parseInt(term.value, 10);
    var apr = num(rate);

    err.textContent = "";
    if (d > p) {
      d = p;
      down.value = p;
      err.textContent = "Down payment cannot be more than the car price.";
    }

    var loan = p - d;
    var r = apr / 100 / 12;
    var monthly = r === 0 ? loan / months : (loan * r) / (1 - Math.pow(1 + r, -months));
    var total = monthly * months;
    var interest = total - loan;

    document.getElementById("monthly").textContent = money(monthly);
    document.getElementById("loan").textContent = money(loan);
    document.getElementById("interest").textContent = money(interest);
    document.getElementById("total").textContent = money(total);
    document.getElementById("grand").textContent = money(total + d);

    applyLink.href = carSel.value === "custom" ? "contact.html" : "contact.html?car=" + carSel.value;

    var pct = total > 0 ? (loan / total) * 100 : 100;
    document.getElementById("bar-p").style.width = pct + "%";
    document.getElementById("bar-i").style.width = 100 - pct + "%";

    var share = p > 0 ? Math.round((d / p) * 100) : 0;
    downRange.value = share;
    downHint.textContent = share + "% of the car price";
  }

  carSel.addEventListener("change", function () {
    var c = getCar(carSel.value);
    if (c) {
      price.value = c.price;
      down.value = Math.round(c.price * 0.2);
    }
    calculate();
  });

  price.addEventListener("input", function () {
    carSel.value = "custom";
    calculate();
  });

  downRange.addEventListener("input", function () {
    down.value = Math.round((num(price) * downRange.value) / 100);
    calculate();
  });

  [down, term, rate].forEach(function (el) {
    el.addEventListener("input", calculate);
  });

  document.getElementById("calc-form").addEventListener("submit", function (e) { e.preventDefault(); });

  calculate();
});
