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
      var enabled = cfg.enabled !== false;
      var number = enabled ? cfg.phone_number || "" : "";
      var hours = cfg.hours || "";
      var failover = cfg.failover || "";
      if (!number) {
        mount.textContent = "";
        var paused = cfg.enabled === false;
        var en = document.createElement("p");
        en.setAttribute("data-pane", "en");
        en.className = "did-meta";
        en.textContent = paused
          ? "Test number paused (abuse guard). Use Talk."
          : "No test number on this host yet. Use Talk.";
        en.hidden = document.documentElement.lang === "ar";
        var ar = document.createElement("p");
        ar.setAttribute("data-pane", "ar");
        ar.className = "did-meta";
        ar.textContent = paused
          ? "رقم الاختبار متوقف (حماية من إساءة الاستخدام). استخدم «تحدّث»."
          : "لا يوجد رقم اختبار على هذا الموقع بعد. استخدم «تحدّث».";
        ar.hidden = document.documentElement.lang !== "ar";
        mount.appendChild(en);
        mount.appendChild(ar);
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
