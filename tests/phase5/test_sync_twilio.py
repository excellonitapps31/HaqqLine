"""Unit tests for Phase 5 Twilio import scaffolding (no network)."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_twilio", ROOT / "scripts/sync_twilio.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_require_voice_number_e164(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.delenv("TWILIO_VOICE_NUMBER", raising=False)
    with pytest.raises(SystemExit):
        sync.require_voice_number()
    monkeypatch.setenv("TWILIO_VOICE_NUMBER", "971500000000")
    with pytest.raises(SystemExit):
        sync.require_voice_number()
    monkeypatch.setenv("TWILIO_VOICE_NUMBER", "+971500000000")
    assert sync.require_voice_number() == "+971500000000"


def test_prefers_standard_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.setenv("TWILIO_API_KEY_SID", "SKaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    monkeypatch.setenv("TWILIO_API_KEY_SECRET", "secret-value")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "should-not-win")
    assert sync.twilio_sid_and_token() == (
        "SKaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "secret-value",
    )


def test_falls_back_to_account_sid(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.delenv("TWILIO_API_KEY_SID", raising=False)
    monkeypatch.delenv("TWILIO_API_KEY_SECRET", raising=False)
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "auth-token")
    assert sync.twilio_sid_and_token() == (
        "ACbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "auth-token",
    )


def test_rejects_non_sk_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.setenv("TWILIO_API_KEY_SID", "ACnotakey")
    monkeypatch.setenv("TWILIO_API_KEY_SECRET", "secret")
    with pytest.raises(SystemExit):
        sync.twilio_sid_and_token()


def test_write_public_keeps_sms_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    public = tmp_path / "public"
    public.mkdir()
    (public / "elevenlabs.json").write_text(
        json.dumps({"agent_id": "agent_5601m1xp22apfdcbwbb8h9y5zzqt"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    sync.write_public("+971500000000", {"phone_number_id": "pn_test"})
    cfg = json.loads((public / "twilio.json").read_text(encoding="utf-8"))
    assert cfg["phone_number"] == "+971500000000"
    assert cfg["inbound_only"] is True
    assert cfg["enable_sms"] is False
    assert cfg["agent_id"].startswith("agent_")
    assert "Twilio 5xx" in cfg["failover"]
