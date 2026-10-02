document.addEventListener("DOMContentLoaded", function () {
  // best: "min" = lowest wins, "max" = highest wins, null = text only
  var ATTRS = [
    { key: "price", label: "Price", best: "min", fmt: formatPrice, on: true },
    { key: "year", label: "Year", best: "max", fmt: String, on: true },
    { key: "mileage", label: "Mileage", best: "min", fmt: formatMiles, on: true },
    { key: "engine", label: "Engine", best: null, fmt: String, on: true },
    { key: "power", label: "Power", best: "max", fmt: function (v) { return v + " hp"; }, on: true },
    { key: "transmission", label: "Transmission", best: null, fmt: String, on: false },
    { key: "fuel", label: "Fuel type", best: null, fmt: String, on: false },
    { key: "mpg", label: "Fuel economy", best: "max", fmt: function (v) { return v + " mpg"; }, on: false },
    { key: "drive", label: "Drive", best: null, fmt: String, on: false },
    { key: "seats", label: "Seats", best: "max", fmt: String, on: false },
    { key: "color", label: "Colour", best: null, fmt: String, on: false }
  ];

  var picks = [0, 1, 2].map(function (i) { return document.getElementById("pick" + i); });
  var attrBox = document.getElementById("attr-list");
  var out = document.getElementById("compare-out");

  picks.forEach(function (sel, i) {
    sel.innerHTML =
      '<option value="">None</option>' +
      CARS.map(function (c) {
        return '<option value="' + c.id + '">' + c.brand + " " + c.model + "</option>";
      }).join("");
    sel.value = CARS[i] ? CARS[i].id : "";
    sel.addEventListener("change", render);
  });

  var first = new URLSearchParams(location.search).get("a");
  if (first && getCar(first)) {
    var others = CARS.filter(function (c) { return c.id !== first; });
    picks[0].value = first;
    picks[1].value = others[0] ? others[0].id : "";
    picks[2].value = others[1] ? others[1].id : "";
  }

  attrBox.innerHTML = ATTRS.map(function (a) {
    return '<label><input type="checkbox" value="' + a.key + '"' + (a.on ? " checked" : "") + "> " + a.label + "</label>";
  }).join("");
  attrBox.addEventListener("change", render);

  function render() {
    var cars = picks
      .map(function (s) { return getCar(s.value); })
      .filter(Boolean);

    var chosen = Array.prototype.slice
      .call(attrBox.querySelectorAll("input:checked"))
      .map(function (i) { return i.value; });
    var attrs = ATTRS.filter(function (a) { return chosen.indexOf(a.key) !== -1; });

    if (cars.length < 2) {
      out.innerHTML = '<div class="table-wrap"><p class="empty">Select at least two cars to compare.</p></div>';
      return;
    }
    if (!attrs.length) {
      out.innerHTML = '<div class="table-wrap"><p class="empty">Tick at least one detail to compare.</p></div>';
      return;
    }

    var head =
      "<thead><tr><th></th>" +
      cars.map(function (c) {
        return (
          "<th><img src=\"" + c.front + "\" alt=\"" + c.brand + " " + c.model + "\">" +
          "<small>" + c.brand + "</small>" + c.model + "</th>"
        );
      }).join("") +
      "</tr></thead>";

    var body = attrs.map(function (a) {
      var winner = null;
      if (a.best) {
        var vals = cars.map(function (c) { return c[a.key]; });
        var target = a.best === "min" ? Math.min.apply(null, vals) : Math.max.apply(null, vals);
        // no highlight when every car ties
        if (vals.some(function (v) { return v !== target; })) winner = target;
      }
      return (
        "<tr><th>" + a.label + "</th>" +
        cars.map(function (c) {
          var text = a.fmt(c[a.key]);
          return "<td>" + (winner !== null && c[a.key] === winner ? '<span class="best">' + text + "</span>" : text) + "</td>";
        }).join("") +
        "</tr>"
      );
    }).join("");

    var actions =
      "<tr><th>Next step</th>" +
      cars.map(function (c) {
        return '<td><a class="btn btn-sm" href="inventory.html#' + c.id + '">Details</a></td>';
      }).join("") +
      "</tr>";

    out.innerHTML = '<div class="table-wrap"><table class="compare-table">' + head + "<tbody>" + body + actions + "</tbody></table></div>";
  }

  render();
});
