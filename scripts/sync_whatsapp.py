#!/usr/bin/env python3
"""Assign the HaqqLine agent to an ElevenLabs WhatsApp account (post Meta Embedded Signup).

Import of a WABA is done in the ElevenLabs dashboard (Meta Embedded Signup).
This script lists accounts, PATCHes assigned_agent_id, and writes public/whatsapp.json.
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.elevenlabs.io"
CTX = ssl.create_default_context()
LABEL = "HaqqLine sandbox WhatsApp"


def api(method: str, path: str, body: dict | None = None) -> dict | list:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=120) as res:
            raw = res.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise SystemExit(f"{method} {path} -> {exc.code}: {detail[:4000]}") from exc


def agent_id() -> str:
    cfg = json.loads((ROOT / "public/elevenlabs.json").read_text(encoding="utf-8"))
    aid = str(cfg.get("agent_id") or "")
    if not aid.startswith("agent_"):
        raise SystemExit("public/elevenlabs.json has no live agent_id")
    return aid


def list_accounts() -> list[dict]:
    listing = api("GET", "/v1/convai/whatsapp-accounts")
    if isinstance(listing, list):
        return listing
    if isinstance(listing, dict):
        return listing.get("whatsapp_accounts") or listing.get("accounts") or listing.get("items") or []
    return []


def pick_account(rows: list[dict]) -> dict:
    phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    e164 = os.environ.get("WHATSAPP_E164", "").strip()
    if phone_id:
        for row in rows:
            if str(row.get("phone_number_id") or "") == phone_id:
                return row
        raise SystemExit(f"No WhatsApp account with phone_number_id={phone_id}")
    if e164:
        if not e164.startswith("+"):
            raise SystemExit("WHATSAPP_E164 must be E.164 (start with +)")
        for row in rows:
            if str(row.get("phone_number") or "") == e164:
                return row
        raise SystemExit(f"No WhatsApp account with phone_number={e164}")
    raise SystemExit(
        "Set WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_E164 after Meta Embedded Signup "
        "imported the WABA into ElevenLabs."
    )


def assign_agent(phone_number_id: str, aid: str) -> dict:
    return api(  # type: ignore[return-value]
        "PATCH",
        f"/v1/convai/whatsapp-accounts/{phone_number_id}",
        {
            "assigned_agent_id": aid,
            "enable_messaging": True,
            "enable_audio_message_response": True,
            "enable_typing_indicator": True,
        },
    )


def wa_me_link(number: str) -> str:
    digits = number.lstrip("+").replace(" ", "")
    return f"https://wa.me/{digits}"


def write_public(row: dict, aid: str) -> None:
    number = str(row.get("phone_number") or "")
    path = ROOT / "public/whatsapp.json"
    path.write_text(
        json.dumps(
            {
                "connected": bool(number),
                "phone_number": number,
                "phone_number_id": str(row.get("phone_number_id") or ""),
                "business_account_id": str(row.get("business_account_id") or ""),
                "wa_me": wa_me_link(number) if number else "",
                "label": LABEL,
                "inbound_messages": True,
                "outbound_templates": False,
                "voice_calls": False,
                "same_agent": True,
                "agent_id": aid,
                "sandbox_disclaimer": (
                    "ExcellonIT sandbox — not a government service. Not DLD, RERA, or RDC. Not legal advice."
                ),
                "stop_policy": (
                    "Reply STOP to opt out of further sandbox WhatsApp messages per Meta policy. "
                    "HELP for help. Human handoff uses escalate_human."
                ),
                "failover": "If WhatsApp is not connected yet, use Talk on this page.",
                "hours": "Sandbox WhatsApp — any hour when connected. Not a government hotline.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def scaffolding_ok() -> dict:
    """Validate committed empty scaffolding (CI skip path)."""
    cfg = json.loads((ROOT / "public/whatsapp.json").read_text(encoding="utf-8"))
    assert cfg.get("connected") is False
    assert cfg.get("phone_number") == ""
    assert cfg.get("voice_calls") is False
    assert cfg.get("outbound_templates") is False
    assert cfg.get("same_agent") is True
    assert "STOP" in (cfg.get("stop_policy") or "")
    assert "sandbox" in (cfg.get("sandbox_disclaimer") or "").lower() or "Sandbox" in (
        cfg.get("sandbox_disclaimer") or ""
    )
    return cfg


def main() -> None:
    if os.environ.get("HAQQLINE_WHATSAPP_SCAFFOLD_ONLY") == "1":
        print(json.dumps({"ok": True, "mode": "scaffold", **scaffolding_ok()}, indent=2))
        return
    aid = agent_id()
    rows = list_accounts()
    row = pick_account(rows)
    phone_number_id = str(row.get("phone_number_id") or "")
    if not phone_number_id:
        raise SystemExit("Account missing phone_number_id")
    updated = assign_agent(phone_number_id, aid)
    merged = {**row, **(updated if isinstance(updated, dict) else {})}
    write_public(merged, aid)
    print(
        json.dumps(
            {
                "ok": True,
                "agent_id": aid,
                "phone_number": merged.get("phone_number"),
                "phone_number_id": phone_number_id,
                "wa_me": wa_me_link(str(merged.get("phone_number") or "")),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
