"""Phase 8 case spine: create, transitions, audit, webhook link."""

from __future__ import annotations

import concurrent.futures
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
SECRET_FILE = ROOT / "public/api/data/elevenlabs_webhook.secret"
SECRET = "test_haqqline_webhook_secret_phase8"


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


def test_confirmed_submit_creates_pending_case(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
    )
    assert status == 200
    assert body["status"] == "pending_human"
    case_id = body["id"]
    st, case = _req(api_base, "GET", f"/api/v1/cases/{case_id}")
    assert st == 200
    assert case["type"] == "filing"
    assert case["status"] == "pending_human"
    assert case["pack_version"] == CFG["pack_version"]
    assert case["citation_id"] == CFG["citation_id"]


def test_status_transitions_and_illegal_rejected(api_base: str) -> None:
    _, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
    )
    case_id = body["id"]
    st, bad = _req(api_base, "PATCH", f"/api/v1/cases/{case_id}", {"status": "closed"})
    assert st == 409
    assert bad["error"] == "illegal_transition"
    st, mid = _req(api_base, "PATCH", f"/api/v1/cases/{case_id}", {"status": "in_review"})
    assert st == 200
    assert mid["status"] == "in_review"
    st, done = _req(api_base, "PATCH", f"/api/v1/cases/{case_id}", {"status": "closed"})
    assert st == 200
    assert done["status"] == "closed"


def test_case_audit_includes_submit_and_is_append_only(api_base: str) -> None:
    _, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "marina"}},
    )
    case_id = body["id"]
    _req(api_base, "PATCH", f"/api/v1/cases/{case_id}", {"status": "in_review"})
    st, audit = _req(api_base, "GET", f"/api/v1/cases/{case_id}/audit")
    assert st == 200
    assert audit["case_id"] == case_id
    assert len(audit["entries"]) >= 1
    assert any(e.get("result", {}).get("case_id") == case_id for e in audit["entries"])
    assert len(audit["events"]) >= 2  # created + status_changed


def test_concurrent_submits_preserve_append_only_audit(api_base: str) -> None:
    """Parallel filings must each leave a distinct case + audit entry (flock)."""

    def one(i: int):
        return _req(
            api_base,
            "POST",
            "/api/v1/tools/submit_to_human_queue",
            {"caller_confirmed": True, "packet": {"area": "jlt", "n": i}},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(one, range(8)))
    ids = []
    for status, body in results:
        assert status == 200
        assert body["status"] == "pending_human"
        ids.append(body["id"])
    assert len(ids) == len(set(ids))
    for case_id in ids:
        st, audit = _req(api_base, "GET", f"/api/v1/cases/{case_id}/audit")
        assert st == 200
        assert any(e.get("result", {}).get("case_id") == case_id for e in audit["entries"])
        assert any(ev.get("event") == "created" for ev in audit["events"])


def test_webhook_links_conversation_to_case(api_base: str, tmp_path=None) -> None:
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(SECRET, encoding="utf-8")
    _, filing = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
    )
    case_id = filing["id"]
    payload = {
        "type": "post_call_transcription",
        "data": {
            "agent_id": "agent_test",
            "conversation_id": "conv_phase8_link",
            "status": "done",
            "transcript": [{"role": "agent", "message": "Sandbox disclosure"}],
        },
    }
    raw = json.dumps(payload, separators=(",", ":"))
    ts = str(int(time.time()))
    digest = "v0=" + hmac.new(SECRET.encode(), f"{ts}.{raw}".encode(), hashlib.sha256).hexdigest()
    data = raw.encode()
    req = urllib.request.Request(
        api_base + "/api/v1/webhooks/elevenlabs",
        data=data,
        headers={
            "Content-Type": "application/json",
            "ElevenLabs-Signature": f"t={ts},{digest}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read().decode())
        assert res.status == 200
        assert body["received"] is True
        assert body["case_id"] == case_id
    st, case = _req(api_base, "GET", f"/api/v1/cases/{case_id}")
    assert st == 200
    assert case["conversation_id"] == "conv_phase8_link"


def test_health_phase_at_least_8(api_base: str) -> None:
    st, body = _req(api_base, "GET", "/api/v1/health", auth=False)
    assert st == 200
    assert body["phase"] >= 8
