"""Phase 10 WhatsApp scaffolding (WABA may be deferred)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "public/index.html").read_text(encoding="utf-8")
JS = (ROOT / "public/whatsapp.js").read_text(encoding="utf-8")
CFG = json.loads((ROOT / "public/whatsapp.json").read_text(encoding="utf-8"))
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))
TESTS = json.loads((ROOT / "elevenlabs/tests.json").read_text(encoding="utf-8"))


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_whatsapp", ROOT / "scripts/sync_whatsapp.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_whatsapp_section_is_sandbox_labelled() -> None:
    assert 'id="whatsapp"' in HTML
    assert 'src="/whatsapp.js"' in HTML
    assert "WhatsApp (sandbox)" in HTML
    assert "واتساب (تجريبي)" in HTML
    assert "not a government WhatsApp" in HTML or "Not a government" in HTML
    assert "Official WABA" in HTML or "ElevenLabs" in HTML
    assert CFG["connected"] is False
    assert CFG["phone_number"] == ""
    assert CFG["voice_calls"] is False
    assert CFG["outbound_templates"] is False
    assert CFG["same_agent"] is True
    assert "STOP" in CFG["stop_policy"]
    assert "sandbox" in CFG["sandbox_disclaimer"].lower()
    assert "Talk" in CFG["failover"]
    assert "/whatsapp.json" in JS
    assert "Use Talk." in JS
    assert "wa.me" in JS
    assert HEALTH["phase"] >= 10
    assert HEALTH["channels"]["whatsapp"] is True
    if HEALTH["phase"] < 11:
        assert HEALTH["channels"]["sms"] is False


def test_empty_whatsapp_falls_back_to_talk() -> None:
    assert "No sandbox WhatsApp number" in JS
    assert "whatsapp-empty" in JS
    assert "whatsapp-number" in JS


def test_gold_scenarios_and_confirm_gate_still_in_agent_suite() -> None:
    names = {row["name"] for row in TESTS}
    assert "haqqline-tool-lookup-jlt" in names
    assert "haqqline-tool-no-unconfirmed-submit" in names
    assert "haqqline-sim-en-jlt-within" in names or "haqqline-sim-en-jlt-overband" in names
    assert "haqqline-sim-ar-jlt-within" in names or "haqqline-sim-ar-overband" in names
    assert "haqqline-sim-en-unconfirmed-file" in names
    assert "haqqline-sim-ar-unconfirmed-file" in names
    assert "haqqline-disclosure-en" in names


def test_stop_opt_out_policy_documented() -> None:
    assert "STOP" in CFG["stop_policy"]
    assert "HELP" in CFG["stop_policy"]
    assert "Meta" in CFG["stop_policy"]
    assert "whatsapp-stop" in JS


def test_sync_scaffold_only_and_wa_me(monkeypatch) -> None:
    sync = load_sync()
    monkeypatch.setenv("HAQQLINE_WHATSAPP_SCAFFOLD_ONLY", "1")
    # scaffolding_ok should not raise
    cfg = sync.scaffolding_ok()
    assert cfg["connected"] is False
    assert sync.wa_me_link("+971501234567") == "https://wa.me/971501234567"


def test_sync_requires_selector_without_secrets(monkeypatch) -> None:
    sync = load_sync()
    monkeypatch.delenv("HAQQLINE_WHATSAPP_SCAFFOLD_ONLY", raising=False)
    monkeypatch.delenv("WHATSAPP_PHONE_NUMBER_ID", raising=False)
    monkeypatch.delenv("WHATSAPP_E164", raising=False)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test_key")
    monkeypatch.setattr(sync, "agent_id", lambda: "agent_test")
    monkeypatch.setattr(sync, "list_accounts", lambda: [])
    try:
        sync.main()
        raised = False
    except SystemExit:
        raised = True
    assert raised
