"""Phase 11 SMS: receipts, STOP, help, no SMS on unconfirmed."""

from __future__ import annotations

import importlib.util
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
HTML = (ROOT / "public/index.html").read_text(encoding="utf-8")
JS = (ROOT / "public/sms.js").read_text(encoding="utf-8")
SMS = json.loads((ROOT / "public/sms.json").read_text(encoding="utf-8"))
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_sms", ROOT / "scripts/sync_sms.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _req(base: str, method: str, path: str, body=None, auth=True, form=None, timeout=10):
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*"}
    else:
        data = None if body is None else json.dumps(body).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + KEY
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            ctype = res.headers.get_content_type()
            if "json" in ctype:
                payload = json.loads(raw.decode()) if raw else {}
            else:
                payload = raw.decode()
            return res.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw.decode()) if raw else {}
        except Exception:
            payload = raw.decode() if raw else {}
        return exc.code, payload


def test_sms_section_sandbox_markup() -> None:
    assert 'id="sms"' in HTML
    assert 'src="/sms.js"' in HTML
    assert "SMS (sandbox fallback)" in HTML
    assert "No rights-check over SMS" in HTML or "no rights-check" in HTML.lower()
    assert SMS["connected"] is False
    assert SMS["phone_number"] == ""
    assert SMS["no_rights_check"] is True
    assert SMS["primary_channel"] == "whatsapp"
    assert "filing_queued" in SMS["events"]
    assert "STOP" in SMS["stop_policy"]
    assert "Use WhatsApp or Talk" in JS
    assert HEALTH["phase"] >= 11
    assert HEALTH["channels"]["sms"] is True


def test_sync_scaffold(monkeypatch) -> None:
    sync = load_sync()
    monkeypatch.setenv("HAQQLINE_SMS_SCAFFOLD_ONLY", "1")
    assert sync.scaffolding_ok()["connected"] is False


def test_filing_queued_writes_outbox_with_case_id(api_base: str) -> None:
    st, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt", "phone": "+971500000011"}},
    )
    assert st == 200
    assert body["status"] == "pending_human"
    case_id = body["id"]
    assert body.get("sms", {}).get("body") and case_id in body["sms"]["body"]
    assert "pending_human" in body["sms"]["body"]
    st, outbox = _req(api_base, "GET", "/api/v1/sms/outbox")
    assert st == 200
    assert any(
        e.get("event") == "filing_queued" and e.get("case_id") == case_id for e in outbox.get("entries", [])
    )


def test_unconfirmed_submit_no_sms(api_base: str) -> None:
    st0, before = _req(api_base, "GET", "/api/v1/sms/outbox")
    assert st0 == 200
    n = len(before.get("entries", []))
    st, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"packet": {"area": "jlt", "phone": "+971500000099"}},
    )
    assert st in (400, 403)
    assert body.get("error") == "confirmation_required" or body.get("policy_denied") is True
    st1, after = _req(api_base, "GET", "/api/v1/sms/outbox")
    assert st1 == 200
    assert len(after.get("entries", [])) == n


def test_stop_blocks_further_sms(api_base: str) -> None:
    phone = "+971500000022"
    st, xml = _req(
        api_base,
        "POST",
        "/api/v1/webhooks/twilio/sms",
        auth=False,
        form={"From": phone, "Body": "STOP", "MessageSid": "SM_test_stop"},
    )
    assert st == 200
    assert "unsubscribed" in xml.lower() or "STOP" in xml or "opt" in xml.lower()
    st, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt", "phone": phone}},
    )
    assert st == 200
    assert body.get("sms", {}).get("skipped") == "opted_out"


def test_invalid_inbound_help_no_submit(api_base: str) -> None:
    st, xml = _req(
        api_base,
        "POST",
        "/api/v1/webhooks/twilio/sms",
        auth=False,
        form={"From": "+971500000033", "Body": "gibberish-please-file", "MessageSid": "SM_bad"},
    )
    assert st == 200
    assert "HELP" in xml or "STATUS" in xml or "WhatsApp" in xml or "Talk" in xml
    assert "submit_to_human_queue" not in xml
    st2, audit = _req(api_base, "GET", "/api/v1/audit")
    assert st2 == 200
    # Latest inbound audited; no accidental tool submit from SMS
    assert any(e.get("tool") == "twilio_sms_inbound" for e in audit.get("entries", []))


def test_health_phase_at_least_11(api_base: str) -> None:
    st, body = _req(api_base, "GET", "/api/v1/health", auth=False)
    assert st == 200
    assert body["phase"] >= 11
