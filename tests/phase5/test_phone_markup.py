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
    assert 'id="call"' in HTML
    assert 'src="/call.js"' in HTML
    assert "failover" in CFG
    assert "Twilio 5xx" in CFG["failover"]
    assert CFG["inbound_only"] is True
    assert CFG["enable_sms"] is False
    assert "/twilio.json" in JS
    assert "Use Talk." in JS
    assert "Test number paused (abuse guard)" in JS
    assert "استخدم «تحدّث»" in JS
    assert "Twilio secrets" not in JS
    assert HEALTH["phase"] >= 5
    assert HEALTH["channels"]["phone"] is True
    if HEALTH["phase"] < 11:
        assert HEALTH["channels"]["sms"] is False
    assert "enabled" in CFG
    assert CFG.get("kill_switch") == "HAQQLINE_CALL_DID_ENABLED" or CFG["phone_number"] == ""


def test_number_not_hardcoded_as_government_line() -> None:
    assert "JustNow" not in HTML
    assert "not a government service" in HTML
    assert CFG["phone_number"] == "" or CFG["phone_number"].startswith("+")
    assert "800" not in CFG["phone_number"]
    assert "04" not in (CFG["phone_number"] or "")


def test_empty_did_falls_back_to_talk() -> None:
    assert "No test number on this host yet" in JS
    assert "tel:" in JS
    assert "test-did-number" in JS
