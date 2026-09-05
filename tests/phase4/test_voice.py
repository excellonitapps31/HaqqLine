from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRET_FILE = ROOT / "public/api/data/elevenlabs_webhook.secret"
SECRET = "test_haqqline_webhook_secret"


def _sign(body: str, ts: str | None = None) -> tuple[str, str]:
    timestamp = ts or str(int(time.time()))
    digest = "v0=" + hmac.new(SECRET.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256).hexdigest()
    return timestamp, f"t={timestamp},{digest}"


def test_widget_markup() -> None:
    html = (ROOT / "public/index.html").read_text(encoding="utf-8")
    js = (ROOT / "public/voice.js").read_text(encoding="utf-8")
    cfg = json.loads((ROOT / "public/elevenlabs.json").read_text(encoding="utf-8"))
    assert "convai-widget-embed" in html
    assert 'id="talk"' in html
    assert "elevenlabs-convai" in js
    assert "agent-id" in js
    assert cfg["widget_script"].endswith("convai-widget-embed")
    prompt = (ROOT / "elevenlabs/prompt.md").read_text(encoding="utf-8")
    assert "AI disclosure" in prompt
    assert "caller_confirmed" in prompt
    tests = json.loads((ROOT / "elevenlabs/tests.json").read_text(encoding="utf-8"))
    names = {row["name"] for row in tests}
    assert "haqqline-tool-no-unconfirmed-submit" in names
    assert len([row for row in tests if row["type"] == "simulation"]) >= 10


def test_webhook_rejects_bad_signature(api_base: str) -> None:
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(SECRET, encoding="utf-8")
    body = json.dumps({"type": "post_call_transcription", "data": {"conversation_id": "c1"}}).encode()
    req = urllib.request.Request(
        api_base + "/api/v1/webhooks/elevenlabs",
        data=body,
        headers={"Content-Type": "application/json", "ElevenLabs-Signature": "t=1,v0=deadbeef"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        raise AssertionError("expected 401")
    except urllib.error.HTTPError as exc:
        assert exc.code == 401


def test_webhook_accepts_valid_hmac(api_base: str) -> None:
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(SECRET, encoding="utf-8")
    payload = {
        "type": "post_call_transcription",
        "data": {
            "agent_id": "agent_test",
            "conversation_id": "conv_sandbox_1",
            "status": "done",
            "transcript": [{"role": "agent", "message": "Sandbox disclosure"}],
        },
    }
    raw = json.dumps(payload, separators=(",", ":"))
    _ts, header = _sign(raw)
    req = urllib.request.Request(
        api_base + "/api/v1/webhooks/elevenlabs",
        data=raw.encode(),
        headers={"Content-Type": "application/json", "ElevenLabs-Signature": header},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read().decode())
        assert res.status == 200
        assert body["received"] is True
        assert body["id"] == "conv_sandbox_1"
