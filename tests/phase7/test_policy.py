"""Phase 7 policy engine: allowlists, credential bans, deny reason codes."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
OPENAPI = json.loads((ROOT / "public/api/v1/openapi.json").read_text(encoding="utf-8"))


def _req(base: str, method: str, path: str, body=None, auth=True, headers=None, timeout=10):
    data = None if body is None else json.dumps(body).encode()
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        hdrs["Authorization"] = "Bearer " + KEY
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(base + path, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            payload = json.loads(raw.decode()) if raw else {}
            return res.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        payload = json.loads(raw.decode()) if raw else {}
        return exc.code, payload


def test_openapi_documents_policy_denied() -> None:
    schema = OPENAPI["components"]["schemas"]["PolicyDenied"]
    reasons = set(schema["properties"]["error"]["enum"])
    for code in (
        "confirmation_required",
        "tool_not_allowed_for_node",
        "forbidden_credential_field",
        "decide_case_forbidden",
    ):
        assert code in reasons
    assert "/api/v1/tools/decide_case" in OPENAPI["paths"]


def test_unconfirmed_submit_is_policy_denied(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": False, "packet": {"area": "jlt"}},
    )
    assert status == 400
    assert body["error"] == "confirmation_required"
    assert body["policy_denied"] is True
    assert body["reason"] == "confirmation_required"


def test_intake_node_cannot_submit(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
        headers={"X-HaqqLine-Workflow-Node": "Intake"},
    )
    assert status == 403
    assert body["policy_denied"] is True
    assert body["reason"] == "tool_not_allowed_for_node"
    assert body["workflow_node"] == "Intake"


def test_filing_node_may_submit_when_confirmed(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
        headers={"X-HaqqLine-Workflow-Node": "Filing"},
    )
    assert status == 200
    assert body["status"] == "pending_human"


def test_forbidden_credential_fields_denied(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/lookup_rera_band",
        {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000, "pin": "1234"},
    )
    assert status == 403
    assert body["policy_denied"] is True
    assert body["reason"] == "forbidden_credential_field"


def test_decide_case_always_denied(api_base: str) -> None:
    status, body = _req(api_base, "POST", "/api/v1/tools/decide_case", {"outcome": "tenant_wins"})
    assert status == 403
    assert body["policy_denied"] is True
    assert body["reason"] == "decide_case_forbidden"


def test_policy_deny_is_audited(api_base: str) -> None:
    _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True},
        headers={"X-HaqqLine-Workflow-Node": "Intake"},
    )
    status, body = _req(api_base, "GET", "/api/v1/audit")
    assert status == 200
    entries = body["entries"]
    assert any(
        e.get("result", {}).get("policy_denied") is True
        and e.get("result", {}).get("reason") == "tool_not_allowed_for_node"
        for e in entries
    )


def test_php_policy_module_lists_reason_codes() -> None:
    text = (ROOT / "public/api/v1/HaqqLinePolicy.php").read_text(encoding="utf-8")
    for code in (
        "confirmation_required",
        "tool_not_allowed_for_node",
        "forbidden_credential_field",
        "decide_case_forbidden",
    ):
        assert code in text
