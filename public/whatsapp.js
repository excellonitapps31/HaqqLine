(function () {
  var mount = document.getElementById("whatsapp-slot");
  if (!mount) {
    return;
  }
  fetch("/whatsapp.json", { cache: "no-store" })
    .then(function (res) {
      return res.json();
    })
    .then(function (cfg) {
      var number = cfg.phone_number || "";
      var waMe = cfg.wa_me || "";
      var failover = cfg.failover || "";
      var disclaimer = cfg.sandbox_disclaimer || "";
      var stopPolicy = cfg.stop_policy || "";
      mount.innerHTML = "";
      if (!number || !cfg.connected) {
        var en = document.createElement("p");
        en.setAttribute("data-pane", "en");
        en.className = "did-meta";
        en.setAttribute("data-testid", "whatsapp-empty");
        en.textContent = "No sandbox WhatsApp number on this host yet. Use Talk.";
        en.hidden = document.documentElement.lang === "ar";
        var ar = document.createElement("p");
        ar.setAttribute("data-pane", "ar");
        ar.className = "did-meta";
        ar.textContent = "لا يوجد رقم واتساب تجريبي على هذا الموقع بعد. استخدم «تحدّث».";
        ar.hidden = document.documentElement.lang !== "ar";
        mount.appendChild(en);
        mount.appendChild(ar);
        if (failover) {
          var f = document.createElement("p");
          f.className = "did-meta";
          f.textContent = failover;
          mount.appendChild(f);
        }
        return;
      }
      var link = document.createElement("a");
      link.href = waMe || ("https://wa.me/" + String(number).replace(/^\+/, ""));
      link.textContent = number;
      link.setAttribute("data-testid", "whatsapp-number");
      link.rel = "noopener noreferrer";
      link.target = "_blank";
      var p = document.createElement("p");
      p.appendChild(link);
      mount.appendChild(p);
      if (disclaimer) {
        var d = document.createElement("p");
        d.className = "did-meta";
        d.textContent = disclaimer;
        mount.appendChild(d);
      }
      if (stopPolicy) {
        var s = document.createElement("p");
        s.className = "did-meta";
        s.setAttribute("data-testid", "whatsapp-stop");
        s.textContent = stopPolicy;
        mount.appendChild(s);
      }
      if (cfg.hours) {
        var h = document.createElement("p");
        h.className = "did-meta";
        h.textContent = cfg.hours;
        mount.appendChild(h);
      }
    })
    .catch(function () {
      mount.textContent = "Could not load WhatsApp sandbox status.";
    });
})();
