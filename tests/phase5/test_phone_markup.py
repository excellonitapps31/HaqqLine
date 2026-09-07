import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "public/index.html").read_text(encoding="utf-8")
JS = (ROOT / "public/call.js").read_text(encoding="utf-8")
CFG = json.loads((ROOT / "public/twilio.json").read_text(encoding="utf-8"))
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))


def test_test_did_is_labelled_sandbox() -> None:
    assert "sandbox test DID" in HTML
    assert "not a DLD" in HTML
    assert "رقم اختبار" in HTML
    assert 'id="test-did"' in HTML
    assert 'src="/call.js"' in HTML
    assert "failover" in CFG
    assert "Twilio 5xx" in CFG["failover"]
    assert CFG["inbound_only"] is True
    assert "/twilio.json" in JS
    assert HEALTH["phase"] >= 5
    assert HEALTH["channels"]["phone"] is True
    assert HEALTH["channels"]["sms"] is False


def test_number_not_hardcoded_as_government_line() -> None:
    assert "JustNow" not in HTML
    assert "not a government service" in HTML
