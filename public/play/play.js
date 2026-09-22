(function () {
  var KEY = document.body.getAttribute("data-api-key") || "";
  var result = document.getElementById("result");
  var ledger = document.getElementById("ledger");
  var lastBand = null;
  var lastView = null;

  var lines = {
    within: {
      en: "Within the band. Cited pack. Not a ruling.",
      ar: "ضمن الحد. الجدول مذكور. ليس حكماً.",
    },
    outside: {
      en: "Outside the band. Cited pack. Not a ruling.",
      ar: "خارج الحد. الجدول مذكور. ليس حكماً.",
    },
    unknown: {
      en: "No band for that area. A person takes the call. No index invented.",
      ar: "لا يوجد حد لهذه المنطقة. يتولى شخص المكالمة. لم يُختلق مؤشر.",
    },
    advice: {
      en: "Handed to a person. The line does not say who wins.",
      ar: "أُحيل إلى شخص. الخط لا يقول من يفوز.",
    },
    blocked: {
      en: "Refused. The caller has not confirmed.",
      ar: "رُفض. المتصل لم يؤكّد.",
    },
    queued: {
      en: "Queued for a person.",
      ar: "أُدرج لدى شخص.",
    },
  };

  function currentLang() {
    return document.documentElement.lang === "ar" ? "ar" : "en";
  }

  function show(kind, lead, detail) {
    result.setAttribute("data-kind", kind);
    result.textContent = "";
    var leadEl = document.createElement("p");
    leadEl.className = "result-lead";
    leadEl.textContent = lead;
    var raw = document.createElement("pre");
    raw.className = "result-raw";
    raw.textContent = detail;
    result.appendChild(leadEl);
    result.appendChild(raw);
  }

  function showView(view) {
    lastView = view;
    var copy = lines[view.key][currentLang()];
    show(view.kind, copy, view.detail);
  }

  function call(path, body) {
    return fetch(path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + KEY,
      },
      body: JSON.stringify(body),
    }).then(function (res) {
      return res.json().then(function (json) {
        return { status: res.status, json: json };
      });
    });
  }

  function formatBand(status, json) {
    if (status === 404) {
      return "HTTP 404\nescalate: " + json.escalate + "\n" + (json.disclaimer || "") + "\nNo index invented.";
    }
    var rows = [
      "HTTP " + status,
      "source: " + json.source,
      "area: " + json.area_label,
      "index_aed: " + json.index_aed,
      "permitted_increase_pct: " + json.permitted_increase_pct,
      "permitted_new_rent_aed: " + json.permitted_new_rent_aed,
      "proposed_is_within_band: " + json.proposed_is_within_band,
      json.disclaimer,
    ];
    return rows.join("\n");
  }

  document.querySelectorAll("[data-scenario]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-scenario");
      if (id === "within") {
        call("/api/v1/tools/lookup_rera_band", {
          area: "jlt",
          current_rent: 80000,
          proposed_rent: 80000,
        }).then(function (out) {
          lastBand = out.json;
          showView({ key: "within", kind: "ok", detail: formatBand(out.status, out.json) });
        });
      } else if (id === "overband") {
        call("/api/v1/tools/lookup_rera_band", {
          area: "jlt",
          current_rent: 80000,
          proposed_rent: 95000,
        }).then(function (out) {
          lastBand = out.json;
          showView({ key: "outside", kind: "ok", detail: formatBand(out.status, out.json) });
        });
      } else if (id === "unknown") {
        call("/api/v1/tools/lookup_rera_band", {
          area: "not_a_real_community",
          current_rent: 80000,
          proposed_rent: 90000,
        }).then(function (out) {
          lastBand = null;
          showView({ key: "unknown", kind: "block", detail: formatBand(out.status, out.json) });
        });
      } else if (id === "advice") {
        call("/api/v1/tools/escalate_human", { reason: "will I win" }).then(function (out) {
          showView({
            key: "advice",
            kind: "ok",
            detail: "HTTP " + out.status + "\nstatus: " + out.json.status + "\nid: " + out.json.id + "\nAdvice is not answered.",
          });
          refreshLedger();
        });
      }
    });
  });

  document.getElementById("file-blocked").addEventListener("click", function () {
    call("/api/v1/tools/submit_to_human_queue", { packet: { label: "SCENARIO-JLT" } }).then(function (out) {
      showView({
        key: "blocked",
        kind: "block",
        detail: "HTTP " + out.status + "\n" + (out.json.error || JSON.stringify(out.json)),
      });
    });
  });

  document.getElementById("file-confirm").addEventListener("click", function () {
    call("/api/v1/tools/submit_to_human_queue", {
      caller_confirmed: true,
      packet: { label: "SCENARIO-JLT", last_band: lastBand },
    }).then(function (out) {
      showView({
        key: "queued",
        kind: "ok",
        detail: "HTTP " + out.status + "\nstatus: " + out.json.status + "\nid: " + out.json.id,
      });
      refreshLedger();
    });
  });

  document.addEventListener("haqqline:lang", function () {
    if (lastView) {
      showView(lastView);
    }
  });

  function refreshLedger() {
    fetch("/api/v1/audit", { headers: { Authorization: "Bearer " + KEY } })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        var rows = (data.entries || []).slice().reverse();
        ledger.textContent = rows
          .map(function (row) {
            return row.timestamp + "  " + row.tool + "  HTTP " + row.status + "  " + JSON.stringify(row.result);
          })
          .join("\n") || "Empty.";
      });
  }

  document.getElementById("refresh-ledger").addEventListener("click", refreshLedger);
  refreshLedger();
})();
