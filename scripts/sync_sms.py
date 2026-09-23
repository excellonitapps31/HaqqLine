#!/usr/bin/env python3
"""Write live public/sms.json after a Twilio SMS-capable number is available.

Scaffold mode (no secrets): validates empty public/sms.json.
Live mode: requires TWILIO_SMS_NUMBER (E.164) and marks connected=true.
Outbound send still uses HaqqLineSms + TWILIO_ACCOUNT_SID/AUTH_TOKEN at runtime.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = "HaqqLine sandbox SMS"


def scaffolding_ok() -> dict:
    cfg = json.loads((ROOT / "public/sms.json").read_text(encoding="utf-8"))
    assert cfg.get("connected") is False
    assert cfg.get("phone_number") == ""
    assert cfg.get("no_rights_check") is True
    assert cfg.get("primary_channel") == "whatsapp"
    assert "filing_queued" in (cfg.get("events") or [])
    assert "STOP" in (cfg.get("stop_policy") or "")
    return cfg


def write_live(number: str) -> dict:
    if not number.startswith("+"):
        raise SystemExit("TWILIO_SMS_NUMBER must be E.164 (start with +)")
    cfg = {
        "connected": True,
        "phone_number": number,
        "label": LABEL,
        "role": "secondary_transactional",
        "primary_channel": "whatsapp",
        "events": ["filing_queued", "escalated"],
        "inbound_commands": ["STATUS <case_id>", "STOP", "HELP"],
        "no_rights_check": True,
        "sandbox_disclaimer": (
            "ExcellonIT sandbox SMS — not a government service. Not DLD, RERA, or RDC. Not legal advice."
        ),
        "stop_policy": (
            "Reply STOP to opt out. HELP for help. Rights-check stays on Talk or WhatsApp."
        ),
        "failover": "If SMS is not connected yet, use WhatsApp or Talk on this page.",
        "hours": "Sandbox SMS receipts — when connected. Not a government hotline.",
        "webhook": "https://haqqline.excellonit.net/api/v1/webhooks/twilio/sms",
    }
    (ROOT / "public/sms.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return cfg


def main() -> None:
    if os.environ.get("HAQQLINE_SMS_SCAFFOLD_ONLY") == "1":
        print(json.dumps({"ok": True, "mode": "scaffold", **scaffolding_ok()}, indent=2))
        return
    number = os.environ.get("TWILIO_SMS_NUMBER", "").strip() or os.environ.get("TWILIO_VOICE_NUMBER", "").strip()
    if not number:
        raise SystemExit(
            "Set TWILIO_SMS_NUMBER (or TWILIO_VOICE_NUMBER) for live SMS, "
            "or HAQQLINE_SMS_SCAFFOLD_ONLY=1 for scaffold check."
        )
    cfg = write_live(number)
    print(json.dumps({"ok": True, "mode": "live", **cfg}, indent=2))


if __name__ == "__main__":
    main()
