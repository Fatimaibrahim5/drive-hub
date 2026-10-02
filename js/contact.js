document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("contact-form");
  var interest = document.getElementById("interest");
  var message = document.getElementById("message");

  interest.innerHTML =
    '<option value="">General enquiry</option>' +
    CARS.map(function (c) {
      return '<option value="' + c.id + '">' + c.brand + " " + c.model + "</option>";
    }).join("");

  var preset = new URLSearchParams(location.search).get("car");
  if (preset && getCar(preset)) {
    var c = getCar(preset);
    interest.value = preset;
    message.value = "Hi, I am interested in the " + c.year + " " + c.brand + " " + c.model + ". Is it still available?";
  }

  function check(id, ok) {
    document.getElementById(id).classList.toggle("invalid", !ok);
    return ok;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var okName = check("f-name", document.getElementById("name").value.trim() !== "");
    var okEmail = check("f-email", /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(document.getElementById("email").value.trim()));
    var okMsg = check("f-message", message.value.trim() !== "");
    if (!(okName && okEmail && okMsg)) return;

    form.reset();
    var box = document.getElementById("success");
    box.classList.add("show");
    box.scrollIntoView({ behavior: "smooth", block: "center" });
  });
});
