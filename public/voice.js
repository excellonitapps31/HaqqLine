(function () {
  var mount = document.getElementById("voice-widget");
  if (!mount) {
    return;
  }
  fetch("/elevenlabs.json", { cache: "no-store" })
    .then(function (res) {
      return res.json();
    })
    .then(function (cfg) {
      if (!cfg.agent_id) {
        mount.textContent = "Voice agent id is not linked yet.";
        return;
      }
      var el = document.createElement("elevenlabs-convai");
      el.setAttribute("agent-id", cfg.agent_id);
      el.setAttribute("variant", "expanded");
      el.setAttribute("action-text", "Talk");
      el.setAttribute("start-call-text", "Start");
      el.setAttribute("end-call-text", "End");
      el.setAttribute("data-testid", "elevenlabs-widget");
      mount.appendChild(el);
    })
    .catch(function () {
      mount.textContent = "Voice widget failed to load.";
    });
})();
