(function () {
  var mount = document.getElementById("test-did");
  if (!mount) {
    return;
  }
  fetch("/twilio.json", { cache: "no-store" })
    .then(function (res) {
      return res.json();
    })
    .then(function (cfg) {
      var number = cfg.phone_number || "";
      var hours = cfg.hours || "";
      var failover = cfg.failover || "";
      if (!number) {
        mount.textContent = "Test DID is not linked yet. Twilio secrets are required.";
        return;
      }
      mount.innerHTML = "";
      var link = document.createElement("a");
      link.href = "tel:" + number;
      link.textContent = number;
      link.setAttribute("data-testid", "test-did-number");
      var p = document.createElement("p");
      p.appendChild(link);
      var h = document.createElement("p");
      h.className = "did-meta";
      h.textContent = hours;
      var f = document.createElement("p");
      f.className = "did-meta";
      f.textContent = failover;
      mount.appendChild(p);
      mount.appendChild(h);
      mount.appendChild(f);
    })
    .catch(function () {
      mount.textContent = "Could not load the test number.";
    });
})();
