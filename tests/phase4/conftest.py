from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


@pytest.fixture(scope="session")
def api_base() -> str:
    env = os.environ.get("HAQQLINE_API_BASE")
    if env:
        yield env.rstrip("/")
        return
    port = _free_port()
    proc = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(ROOT / "public"), str(ROOT / "public" / "router.php")],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import urllib.request

    deadline = time.time() + 8
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/health", timeout=0.3)
            break
        except Exception:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("php server failed")
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait(timeout=5)
