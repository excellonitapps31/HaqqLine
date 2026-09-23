"""Phase 12 hardening: restore drill, load gate, deps, runbook, rate limit."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
BUDGETS = json.loads((ROOT / "public/sre-budgets.json").read_text(encoding="utf-8"))
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))


def _req(base: str, method: str, path: str, body=None, auth=True, timeout=10):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + KEY
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            return res.status, (json.loads(raw.decode()) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw.decode()) if raw else {}
        except Exception:
            payload = {}
        return exc.code, payload


def test_health_phase_at_least_12() -> None:
    assert HEALTH["phase"] >= 12
    assert (ROOT / "docs/OPERATOR_RUNBOOK.md").is_file()
    assert (ROOT / "docs/NGINX_SECURITY_HEADERS.md").is_file()
    assert (ROOT / "LICENSE").is_file()
    assert "load" in BUDGETS
    assert BUDGETS["load"]["api_rps_sandbox"]["target"] >= 1


def test_restore_drill_artifact(tmp_path=None) -> None:
    subprocess.check_call(["python3", str(ROOT / "scripts/backup_restore_drill.py")], cwd=str(ROOT))
    art = json.loads((ROOT / "reports/phase-12-restore.json").read_text(encoding="utf-8"))
    assert art["ok"] is True
    assert art["phase"] == 12
    assert art["environment"] == "sandbox"
    assert art["elapsed_ms"] >= 0
    assert "cases.jsonl" in art["files"]


def test_deps_licence_scan() -> None:
    subprocess.check_call(["python3", str(ROOT / "scripts/deps_licence_scan.py")], cwd=str(ROOT))
    art = json.loads((ROOT / "reports/phase-12-deps.json").read_text(encoding="utf-8"))
    assert art["ok"] is True
    names = {d["name"] for d in art["direct_dev_dependencies"]}
    assert "pytest" in names
    assert art["runtime"]["php"]


def test_load_sample_meets_sandbox_gate() -> None:
    port_sock = socket.socket()
    port_sock.bind(("127.0.0.1", 0))
    port = int(port_sock.getsockname()[1])
    port_sock.close()
    env = os.environ.copy()
    env["HAQQLINE_DISABLE_RATE_LIMIT"] = "1"
    proc = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(ROOT / "public"), str(ROOT / "public" / "router.php")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 8
        while time.time() < deadline:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/health", timeout=0.3)
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise AssertionError("php server failed")
        env["HAQQLINE_API_BASE"] = f"http://127.0.0.1:{port}"
        env["HAQQLINE_LOAD_WORKERS"] = "4"
        env["HAQQLINE_LOAD_REQUESTS"] = "20"
        subprocess.check_call(["python3", str(ROOT / "scripts/load_test.py")], cwd=str(ROOT), env=env)
        art = json.loads((ROOT / "reports/phase-12-load.json").read_text(encoding="utf-8"))
        assert art["meets_sandbox_gate"] is True
        assert art["success_rate"] >= BUDGETS["load"]["success_rate_min"]["target"]
        assert art["environment"] == "sandbox"
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_rate_limit_enforced_when_enabled() -> None:
    port_sock = socket.socket()
    port_sock.bind(("127.0.0.1", 0))
    port = int(port_sock.getsockname()[1])
    port_sock.close()
    env = os.environ.copy()
    env.pop("HAQQLINE_DISABLE_RATE_LIMIT", None)
    # Force a tiny limit via temporary config would be invasive; instead
    # blast past 120 quickly with many parallel requests without disable flag.
    proc = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(ROOT / "public"), str(ROOT / "public" / "router.php")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 8
        while time.time() < deadline:
            try:
                urllib.request.urlopen(f"{base}/api/v1/health", timeout=0.3)
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise AssertionError("php server failed")
        # Clear prior bucket for this IP if present
        for p in (ROOT / "public/api/data").glob("rate-*.json"):
            p.unlink(missing_ok=True)
        statuses = []
        for i in range(130):
            st, _ = _req(
                base,
                "POST",
                "/api/v1/tools/lookup_rera_band",
                {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000, "i": i},
            )
            statuses.append(st)
            if st == 429:
                break
        assert 429 in statuses
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_runbook_has_dry_run_checklist() -> None:
    text = (ROOT / "docs/OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")
    assert "Phase 12 dry-run checklist" in text
    assert "backup_restore_drill" in text
    assert "load_test" in text
    assert "NGINX_SECURITY_HEADERS" in text
