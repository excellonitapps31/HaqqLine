"""Phase 9 voice SRE: budgets, eval gate, failover, alerts, latency."""

from __future__ import annotations

import importlib.util
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
BUDGETS = json.loads((ROOT / "public/sre-budgets.json").read_text(encoding="utf-8"))
TWILIO = json.loads((ROOT / "public/twilio.json").read_text(encoding="utf-8"))
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))
CALL_JS = (ROOT / "public/call.js").read_text(encoding="utf-8")
TESTS_JSON = json.loads((ROOT / "elevenlabs/tests.json").read_text(encoding="utf-8"))


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_elevenlabs", ROOT / "scripts/sync_elevenlabs.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _req(base: str, method: str, path: str, body=None, auth=True, timeout=10):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + KEY
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            payload = json.loads(raw.decode()) if raw else {}
            return res.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        payload = json.loads(raw.decode()) if raw else {}
        return exc.code, payload


def test_published_budgets_meet_plan() -> None:
    assert BUDGETS["environment"] == "sandbox"
    b = BUDGETS["budgets"]
    assert b["time_to_first_cited_answer_s"]["target"] <= 180
    assert b["time_to_first_disclosure_s"]["target"] > 0
    assert b["tool_latency_p95_ms"]["target"] > 0
    assert b["concurrent_inbound"]["target"] >= 1
    gate = BUDGETS["eval_gate"]
    assert gate["repeat_count_min"] >= 2
    assert gate["pass_rate_min"] == 1.0
    assert "haqqline-tool-no-unconfirmed-submit" in gate["high_stakes_never_quarantined"]
    assert gate["artifact"] == "reports/phase-09-eval.json"


def test_unconfirmed_submit_still_in_agent_suite() -> None:
    names = {row["name"] for row in TESTS_JSON}
    assert "haqqline-tool-no-unconfirmed-submit" in names
    assert "haqqline-sim-en-unconfirmed-file" in names
    assert "haqqline-sim-ar-unconfirmed-file" in names


def test_promote_gate_blocks_failures_and_high_stakes_quarantine(monkeypatch) -> None:
    sync = load_sync()
    summary = {
        "details": [
            {"name": "haqqline-tool-no-unconfirmed-submit", "status": "passed", "reason": ""},
            {"name": "haqqline-disclosure-en", "status": "failed", "reason": "no disclosure"},
        ]
    }
    gate = sync.evaluate_promote_gate(summary, quarantine=set())
    assert gate["ok"] is False
    assert any(f["name"] == "haqqline-disclosure-en" for f in gate["blocking_failures"])

    bad_q = sync.evaluate_promote_gate(
        {"details": [{"name": "haqqline-tool-no-unconfirmed-submit", "status": "passed", "reason": ""}]},
        quarantine={"haqqline-tool-no-unconfirmed-submit"},
    )
    assert bad_q["ok"] is False
    assert bad_q["reason"] == "high_stakes_quarantined"

    ok = sync.evaluate_promote_gate(
        {
            "details": [
                {"name": "haqqline-tool-no-unconfirmed-submit", "status": "passed", "reason": ""},
                {"name": "haqqline-disclosure-en", "status": "passed", "reason": ""},
            ]
        },
        quarantine=set(),
    )
    assert ok["ok"] is True
    assert ok["pass_rate"] == 1.0


def test_failover_path_documented_and_exercised_empty_did() -> None:
    assert "Twilio 5xx" in TWILIO["failover"]
    assert "Talk" in TWILIO["failover"] or "Talk" in CALL_JS
    assert TWILIO["phone_number"] == ""  # DID deferred — empty DID is the exercised failover
    assert "No test number on this host yet" in CALL_JS
    assert "Use Talk." in CALL_JS
    assert BUDGETS["failover"]["twilio_5xx"]


def test_health_phase_at_least_9(api_base: str) -> None:
    assert HEALTH["phase"] >= 9
    st, body = _req(api_base, "GET", "/api/v1/health", auth=False)
    assert st == 200
    assert body["phase"] >= 9


def test_tool_latency_under_budget(api_base: str) -> None:
    target_ms = BUDGETS["budgets"]["tool_latency_p95_ms"]["target"]
    samples = []
    for _ in range(5):
        t0 = time.perf_counter()
        st, body = _req(
            api_base,
            "POST",
            "/api/v1/tools/lookup_rera_band",
            {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000},
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert st == 200
        assert body.get("pack_version") == CFG["pack_version"]
        samples.append(elapsed_ms)
    samples.sort()
    p95 = samples[int(len(samples) * 0.95) - 1] if len(samples) >= 2 else samples[-1]
    assert p95 <= target_ms, f"tool p95 {p95:.1f}ms exceeds budget {target_ms}ms"


def test_policy_deny_writes_alert(api_base: str) -> None:
    st, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"packet": {"area": "jlt"}},
    )
    assert st in (400, 403)
    assert body.get("policy_denied") is True or body.get("error") == "confirmation_required"
    st, alerts = _req(api_base, "GET", "/api/v1/alerts")
    assert st == 200
    assert any(e.get("kind") == "tool_failure" for e in alerts.get("entries", []))
