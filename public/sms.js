(function () {
  var mount = document.getElementById("sms-slot");
  if (!mount) {
    return;
  }
  fetch("/sms.json", { cache: "no-store" })
    .then(function (res) {
      return res.json();
    })
    .then(function (cfg) {
      var number = cfg.phone_number || "";
      mount.innerHTML = "";
      if (!number || !cfg.connected) {
        var en = document.createElement("p");
        en.setAttribute("data-pane", "en");
        en.className = "did-meta";
        en.setAttribute("data-testid", "sms-empty");
        en.textContent = "No sandbox SMS number on this host yet. Use WhatsApp or Talk.";
        en.hidden = document.documentElement.lang === "ar";
        var ar = document.createElement("p");
        ar.setAttribute("data-pane", "ar");
        ar.className = "did-meta";
        ar.textContent = "لا يوجد رقم رسائل نصية تجريبي بعد. استخدم واتساب أو «تحدّث».";
        ar.hidden = document.documentElement.lang !== "ar";
        mount.appendChild(en);
        mount.appendChild(ar);
        if (cfg.failover) {
          var f = document.createElement("p");
          f.className = "did-meta";
          f.textContent = cfg.failover;
          mount.appendChild(f);
        }
        return;
      }
      var p = document.createElement("p");
      p.setAttribute("data-testid", "sms-number");
      p.textContent = number;
      mount.appendChild(p);
      ["sandbox_disclaimer", "stop_policy", "hours"].forEach(function (key) {
        if (cfg[key]) {
          var row = document.createElement("p");
          row.className = "did-meta";
          if (key === "stop_policy") {
            row.setAttribute("data-testid", "sms-stop");
          }
          row.textContent = cfg[key];
          mount.appendChild(row);
        }
      });
    })
    .catch(function () {
      mount.textContent = "Could not load SMS sandbox status.";
    });
})();
