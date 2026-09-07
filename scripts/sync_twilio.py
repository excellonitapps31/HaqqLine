#!/usr/bin/env python3
"""Import a Twilio Voice test DID into ElevenLabs and assign the HaqqLine agent."""

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
LABEL = "HaqqLine sandbox test DID"


def api(method: str, path: str, body: dict | None = None) -> dict:
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


def require_env(*names: str) -> dict[str, str]:
    out = {}
    missing = []
    for name in names:
        value = os.environ.get(name, "").strip()
        if not value:
            missing.append(name)
        else:
            out[name] = value
    if missing:
        raise SystemExit(
            "Phase 5 entry criteria missing GitHub secrets: "
            + ", ".join(missing)
            + ". Also confirm the number is a sandbox test DID, not a DLD/RERA line."
        )
    return out


def agent_id() -> str:
    cfg = json.loads((ROOT / "public/elevenlabs.json").read_text(encoding="utf-8"))
    aid = str(cfg.get("agent_id") or "")
    if not aid.startswith("agent_"):
        raise SystemExit("public/elevenlabs.json has no live agent_id")
    return aid


def upsert_number(number: str, sid: str, token: str, aid: str) -> dict:
    listing = api("GET", "/v1/convai/phone-numbers")
    rows = listing if isinstance(listing, list) else listing.get("phone_numbers") or listing.get("items") or []
    existing = None
    for row in rows:
        if row.get("phone_number") == number or row.get("label") == LABEL:
            existing = row
            break
    if existing:
        pid = existing.get("phone_number_id") or existing.get("id")
        api("PATCH", f"/v1/convai/phone-numbers/{pid}", {"agent_id": aid})
        return {"phone_number_id": pid, "phone_number": number, "created": False}
    created = api(
        "POST",
        "/v1/convai/phone-numbers",
        {
            "provider": "twilio",
            "label": LABEL,
            "phone_number": number,
            "sid": sid,
            "token": token,
            "agent_id": aid,
            "enable_sms": False,
        },
    )
    pid = created.get("phone_number_id") or created.get("id")
    return {"phone_number_id": pid, "phone_number": number, "created": True}


def write_public(number: str, meta: dict) -> None:
    path = ROOT / "public/twilio.json"
    path.write_text(
        json.dumps(
            {
                "phone_number": number,
                "label": LABEL,
                "inbound_only": True,
                "hours": "Sandbox test DID — any hour. Not a government hotline.",
                "failover": "If this number does not ring, use Talk on this page. Twilio 5xx is not a second product.",
                "phone_number_id": meta.get("phone_number_id") or "",
                "agent_id": agent_id(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    env = require_env("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_VOICE_NUMBER")
    number = env["TWILIO_VOICE_NUMBER"]
    if not number.startswith("+"):
        raise SystemExit("TWILIO_VOICE_NUMBER must be E.164 (start with +)")
    aid = agent_id()
    meta = upsert_number(number, env["TWILIO_ACCOUNT_SID"], env["TWILIO_AUTH_TOKEN"], aid)
    write_public(number, meta)
    print(json.dumps({"ok": True, "agent_id": aid, **meta}, indent=2))


if __name__ == "__main__":
    main()
