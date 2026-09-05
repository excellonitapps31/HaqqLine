from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = json.loads((ROOT / "public/api/v1/openapi.json").read_text(encoding="utf-8"))
KEY = json.loads((ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8"))["demo_api_key"]


def _base() -> str:
    return os.environ.get("HAQQLINE_API_BASE", "http://127.0.0.1:8787")


def _req(method: str, path: str, body=None, auth=True, timeout=10):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + KEY
    req = urllib.request.Request(_base() + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            payload = json.loads(raw.decode()) if raw else {}
            return res.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        payload = json.loads(raw.decode()) if raw else {}
        return exc.code, payload


def test_openapi_lists_required_tools() -> None:
    paths = OPENAPI["paths"]
    for path in (
        "/api/v1/tools/lookup_rera_band",
        "/api/v1/tools/lookup_ejari",
        "/api/v1/tools/submit_to_human_queue",
        "/api/v1/tools/escalate_human",
        "/api/v1/health",
        "/api/v1/audit",
    ):
        assert path in paths
    assert OPENAPI["openapi"].startswith("3.1")


def test_auth_rejected_without_key() -> None:
    status, body = _req("POST", "/api/v1/tools/lookup_rera_band", {"area": "jlt", "current_rent": 1, "proposed_rent": 1}, auth=False)
    assert status == 401
    assert body["error"] == "unauthorized"


def test_unknown_area_escalates_without_index() -> None:
    status, body = _req(
        "POST",
        "/api/v1/tools/lookup_rera_band",
        {"area": "not_a_real_community", "current_rent": 80000, "proposed_rent": 90000},
    )
    assert status == 404
    assert body["escalate"] is True
    assert "index_aed" not in body
    assert "invented" not in body or body.get("invented") is not True


def test_known_area_cites_pack() -> None:
    status, body = _req(
        "POST",
        "/api/v1/tools/lookup_rera_band",
        {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000},
    )
    assert status == 200
    assert body["source"]
    assert body["proposed_is_within_band"] is True
    assert "Not legal advice" in body["disclaimer"]


def test_ejari_found_and_missing() -> None:
    ok, found = _req("POST", "/api/v1/tools/lookup_ejari", {"ejari_id": "EJ-1001"})
    assert ok == 200
    assert found["found"] is True
    assert found["invented"] is False
    miss_status, missing = _req("POST", "/api/v1/tools/lookup_ejari", {"ejari_id": "EJ-9999"})
    assert miss_status == 200
    assert missing["found"] is False
    assert missing["invented"] is False
    assert "annual_rent_aed" not in missing


def test_confirmation_gate() -> None:
    denied, body = _req("POST", "/api/v1/tools/submit_to_human_queue", {"packet": {"area": "jlt"}})
    assert denied == 400
    assert body["error"] == "confirmation_required"
    ok, queued = _req(
        "POST",
        "/api/v1/tools/submit_to_human_queue",
        {"caller_confirmed": True, "packet": {"area": "jlt"}},
    )
    assert ok == 200
    assert queued["status"] == "pending_human"


def test_escalate_pending_human() -> None:
    status, body = _req("POST", "/api/v1/tools/escalate_human", {"reason": "will I win"})
    assert status == 200
    assert body["status"] == "pending_human"


def test_load_smoke_documented_demo_rps() -> None:
    """Demo target is 2 r/s. Twenty sequential lookups must succeed."""
    start = time.perf_counter()
    for _ in range(20):
        status, _body = _req(
            "POST",
            "/api/v1/tools/lookup_rera_band",
            {"area": "al_barsha", "current_rent": 70000, "proposed_rent": 70000},
        )
        assert status == 200
    elapsed = time.perf_counter() - start
    assert elapsed < 15
