from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.request
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
    if payload["phase"] >= 5:
        assert channels["phone"] is True
    if payload["phase"] >= 10:
        assert channels["whatsapp"] is True
    else:
        assert channels["whatsapp"] is False
    if payload["phase"] >= 11:
        assert channels["sms"] is True
    else:
        assert channels["sms"] is False
    json.dumps(payload)


def test_health_url_returns_the_same_json() -> None:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    proc = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(ROOT / "public"), str(ROOT / "public" / "router.php")],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 8
        last = None
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=0.5) as res:
                    body = json.loads(res.read().decode())
                    assert res.status == 200
                    assert res.headers.get_content_type() == "application/json"
                    assert body["status"] == "ok"
                    assert body["phase"] >= 1
                    return
            except Exception as exc:
                last = exc
                time.sleep(0.1)
        raise AssertionError(last)
    finally:
        proc.terminate()
        proc.wait(timeout=5)
