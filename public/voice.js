(function () {
  var mount = document.getElementById("voice-widget");
  if (!mount) {
    return;
  }

  var labels = {
    en: { action: "Talk", start: "Start", end: "End" },
    ar: { action: "تحدّث", start: "ابدأ", end: "إنهاء" },
  };
  var lang = document.documentElement.lang === "ar" ? "ar" : "en";
  var agentId = "";

  function render() {
    if (!agentId) {
      return;
    }
    var copy = labels[lang] || labels.en;
    var el = document.createElement("elevenlabs-convai");
    el.setAttribute("agent-id", agentId);
    el.setAttribute("variant", "expanded");
    el.setAttribute("action-text", copy.action);
    el.setAttribute("start-call-text", copy.start);
    el.setAttribute("end-call-text", copy.end);
    el.setAttribute("data-testid", "elevenlabs-widget");
    mount.textContent = "";
    mount.appendChild(el);
  }

  document.addEventListener("haqqline:lang", function (event) {
    var next = event.detail && event.detail.lang === "ar" ? "ar" : "en";
    if (next === lang && mount.querySelector("elevenlabs-convai")) {
      return;
    }
    lang = next;
    render();
  });

  fetch("/elevenlabs.json", { cache: "no-store" })
    .then(function (res) {
      return res.json();
    })
    .then(function (cfg) {
      if (!cfg.agent_id) {
        mount.textContent = "Voice agent id is not linked yet.";
        return;
      }
      agentId = cfg.agent_id;
      render();
    })
    .catch(function () {
      mount.textContent = "Voice widget failed to load.";
    });
})();
