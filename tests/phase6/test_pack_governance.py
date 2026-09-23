"""Phase 6 pack governance: citations, lock hash, band fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]
CITATION = CFG["citation_id"]
VERSION = CFG["pack_version"]


def _req(base: str, method: str, path: str, body=None, auth=True, timeout=10):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + KEY
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            payload = json.loads(raw.decode()) if raw else {}
            return res.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        payload = json.loads(raw.decode()) if raw else {}
        return exc.code, payload


def test_pack_manifest_fields() -> None:
    assert CFG["pack_id"] == "sandbox_decree_43_2013_table_v1"
    assert CFG["pack_version"] == "1.0.0"
    assert CFG["citation_id"] == f"{CFG['pack_id']}@{CFG['pack_version']}"
    assert CFG["content_hash"].startswith("sha256:")
    assert CFG["effective_from"]
    assert "signature" in CFG


def test_pack_lock_script_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_pack_lock.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)
    assert body["ok"] is True
    assert body["citation_id"] == CITATION


def test_lookup_returns_pack_citation(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/lookup_rera_band",
        {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000},
    )
    assert status == 200
    assert body["pack_id"] == CFG["pack_id"]
    assert body["pack_version"] == VERSION
    assert body["citation_id"] == CITATION
    assert body["source"] == CFG["pack_id"]


def test_unknown_area_still_cites_pack_and_does_not_invent(api_base: str) -> None:
    status, body = _req(
        api_base,
        "POST",
        "/api/v1/tools/lookup_rera_band",
        {"area": "not_a_real_community", "current_rent": 80000, "proposed_rent": 90000},
    )
    assert status == 404
    assert body["escalate"] is True
    assert "index_aed" not in body
    assert body["citation_id"] == CITATION
    assert body.get("invented") is not True


def test_band_fixtures_for_signed_pack(api_base: str) -> None:
    fixtures = [
        ("jlt", 80000, 80000, 0, True),
        ("jlt", 80000, 95000, 0, False),
        ("downtown_dubai", 100000, 110000, 10, True),
    ]
    for area, current, proposed, pct, within in fixtures:
        status, body = _req(
            api_base,
            "POST",
            "/api/v1/tools/lookup_rera_band",
            {"area": area, "current_rent": current, "proposed_rent": proposed},
        )
        assert status == 200, (area, body)
        assert body["permitted_increase_pct"] == pct
        assert body["proposed_is_within_band"] is within
        assert body["citation_id"] == CITATION


def test_health_exposes_pack_version(api_base: str) -> None:
    status, body = _req(api_base, "GET", "/api/v1/health", auth=False)
    assert status == 200
    assert body["pack_id"] == CFG["pack_id"]
    assert body["pack_version"] == VERSION
    assert body["citation_id"] == CITATION
    assert body["phase"] >= 6


def test_prompt_requires_citation_id() -> None:
    prompt = (ROOT / "elevenlabs/prompt.md").read_text(encoding="utf-8")
    assert "citation_id" in prompt
