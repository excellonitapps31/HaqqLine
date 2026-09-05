(function () {
  var KEY = document.body.getAttribute("data-api-key") || "";
  var result = document.getElementById("result");
  var ledger = document.getElementById("ledger");
  var lastBand = null;

  function show(kind, text) {
    result.setAttribute("data-kind", kind);
    result.textContent = text;
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
    var lines = [
      "HTTP " + status,
      "source: " + json.source,
      "area: " + json.area_label,
      "index_aed: " + json.index_aed,
      "permitted_increase_pct: " + json.permitted_increase_pct,
      "permitted_new_rent_aed: " + json.permitted_new_rent_aed,
      "proposed_is_within_band: " + json.proposed_is_within_band,
      json.disclaimer,
    ];
    return lines.join("\n");
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
          show("ok", formatBand(out.status, out.json));
        });
      } else if (id === "overband") {
        call("/api/v1/tools/lookup_rera_band", {
          area: "jlt",
          current_rent: 80000,
          proposed_rent: 95000,
        }).then(function (out) {
          lastBand = out.json;
          show("ok", formatBand(out.status, out.json));
        });
      } else if (id === "unknown") {
        call("/api/v1/tools/lookup_rera_band", {
          area: "not_a_real_community",
          current_rent: 80000,
          proposed_rent: 90000,
        }).then(function (out) {
          lastBand = null;
          show("block", formatBand(out.status, out.json));
        });
      } else if (id === "advice") {
        call("/api/v1/tools/escalate_human", { reason: "will I win" }).then(function (out) {
          show("ok", "HTTP " + out.status + "\nstatus: " + out.json.status + "\nid: " + out.json.id + "\nAdvice is not answered.");
          refreshLedger();
        });
      }
    });
  });

  document.getElementById("file-blocked").addEventListener("click", function () {
    call("/api/v1/tools/submit_to_human_queue", { packet: { label: "SCENARIO-JLT" } }).then(function (out) {
      show("block", "HTTP " + out.status + "\n" + (out.json.error || JSON.stringify(out.json)));
    });
  });

  document.getElementById("file-confirm").addEventListener("click", function () {
    call("/api/v1/tools/submit_to_human_queue", {
      caller_confirmed: true,
      packet: { label: "SCENARIO-JLT", last_band: lastBand },
    }).then(function (out) {
      show("ok", "HTTP " + out.status + "\nstatus: " + out.json.status + "\nid: " + out.json.id);
      refreshLedger();
    });
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
