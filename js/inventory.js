document.addEventListener("DOMContentLoaded", function () {
  var list = document.getElementById("inventory-list");
  var chipBox = document.getElementById("brand-chips");
  var sortSel = document.getElementById("sort");
  var brand = "all";

  var brands = [];
  CARS.forEach(function (c) { if (brands.indexOf(c.brand) === -1) brands.push(c.brand); });
  chipBox.innerHTML = brands.map(function (b) {
    return '<button class="chip" type="button" data-brand="' + b + '">' + b + "</button>";
  }).join("");

  document.querySelector(".filters").addEventListener("click", function (e) {
    var chip = e.target.closest(".chip");
    if (!chip) return;
    brand = chip.dataset.brand;
    document.querySelectorAll(".chip").forEach(function (c) { c.classList.toggle("on", c === chip); });
    render();
  });
  sortSel.addEventListener("change", render);

  function row(label, value) {
    return "<tr><th>" + label + "</th><td>" + value + "</td></tr>";
  }

  function render() {
    var cars = CARS.filter(function (c) { return brand === "all" || c.brand === brand; });
    var s = sortSel.value;
    if (s === "price-asc") cars.sort(function (a, b) { return a.price - b.price; });
    if (s === "price-desc") cars.sort(function (a, b) { return b.price - a.price; });
    if (s === "mileage") cars.sort(function (a, b) { return a.mileage - b.mileage; });
    if (s === "year") cars.sort(function (a, b) { return b.year - a.year; });

    list.innerHTML = cars.map(function (c) {
      return (
        '<article class="inv-car" id="' + c.id + '">' +
          '<div>' +
            '<div class="gallery-main"><img src="' + c.front + '" alt="' + c.brand + ' ' + c.model + '"></div>' +
            '<div class="thumbs">' +
              '<button type="button" class="on" data-src="' + c.front + '" aria-label="Front view"><img src="' + c.front + '" alt=""></button>' +
              '<button type="button" data-src="' + c.back + '" aria-label="Rear view"><img src="' + c.back + '" alt=""></button>' +
              (c.interior ? '<button type="button" data-src="' + c.interior + '" aria-label="Interior view"><img src="' + c.interior + '" alt=""></button>' : '') +
            '</div>' +
          '</div>' +
          '<div class="inv-info">' +
            '<p class="brand">' + c.brand + '</p>' +
            '<h2>' + c.model + '</h2>' +
            '<div class="price-tag">' + formatPrice(c.price) + '</div>' +
            '<table class="spec-table">' +
              row("Year", c.year) +
              row("Mileage", formatMiles(c.mileage)) +
              row("Engine", c.engine) +
              row("Power", c.power + " hp") +
              row("Transmission", c.transmission) +
              row("Fuel type", c.fuel) +
              row("Drive", c.drive) +
              row("Colour", c.color) +
            '</table>' +
            '<h3>Specification</h3>' +
            '<ul class="feature-list">' + c.specs.map(function (f) { return "<li>" + f + "</li>"; }).join("") + '</ul>' +
            '<h3>Description</h3>' +
            '<p class="desc">' + c.description + '</p>' +
            '<div class="btn-row">' +
              '<a class="btn" href="contact.html?car=' + c.id + '">Contact us</a>' +
              '<a class="btn btn-ghost" href="finCal.html?car=' + c.id + '">Finance this car</a>' +
              '<a class="btn btn-ghost" href="compare.html?a=' + c.id + '">Compare</a>' +
            '</div>' +
          '</div>' +
        '</article>'
      );
    }).join("");
  }

  list.addEventListener("click", function (e) {
    var btn = e.target.closest(".thumbs button");
    if (!btn) return;
    var wrap = btn.closest(".inv-car");
    wrap.querySelector(".gallery-main img").src = btn.dataset.src;
    wrap.querySelectorAll(".thumbs button").forEach(function (b) { b.classList.toggle("on", b === btn); });
  });

  render();

  if (location.hash) {
    var target = document.getElementById(location.hash.slice(1));
    if (target) {
      setTimeout(function () {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        target.classList.add("highlight");
      }, 150);
    }
  }
});
