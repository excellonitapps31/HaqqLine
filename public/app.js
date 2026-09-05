(function () {
  var storageKey = "haqqline-lang";
  var buttons = document.querySelectorAll("[data-lang-switch]");

  function apply(lang) {
    var next = lang === "ar" ? "ar" : "en";
    document.documentElement.lang = next === "ar" ? "ar" : "en";
    document.documentElement.dir = next === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-pane]").forEach(function (el) {
      el.hidden = el.getAttribute("data-pane") !== next;
    });
    buttons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-lang-switch") === next));
    });
    try {
      localStorage.setItem(storageKey, next);
    } catch (e) {
      /* ignore */
    }
    document.dispatchEvent(new CustomEvent("haqqline:lang", { detail: { lang: next } }));
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      apply(btn.getAttribute("data-lang-switch"));
    });
  });

  var initial = "en";
  try {
    initial = localStorage.getItem(storageKey) || initial;
  } catch (e) {
    /* ignore */
  }
  apply(initial);
})();
