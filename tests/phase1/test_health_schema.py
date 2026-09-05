from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEALTH = ROOT / "public" / "health.json"

REQUIRED = {
    "status": "ok",
    "service": "haqqline",
    "product": "HaqqLine",
    "vendor": "ExcellonIT",
    "environment": "sandbox",
    "host": "haqqline.excellonit.net",
}


def test_health_is_strict_json_object() -> None:
    payload = json.loads(HEALTH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    for key, value in REQUIRED.items():
        assert payload[key] == value
    assert payload["phase"] >= 1
    channels = payload["channels"]
    assert channels["web_shell"] is True
    if payload["phase"] >= 4:
        assert channels["voice"] is True
    else:
        assert channels["voice"] is False
    assert channels["whatsapp"] is False
    assert channels["sms"] is False
    json.dumps(payload)
