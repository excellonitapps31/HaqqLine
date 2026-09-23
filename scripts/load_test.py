#!/usr/bin/env python3
"""Sandbox-labelled concurrent API load sample (Phase 12).

Hits lookup_rera_band with N workers for M requests each.
Writes reports/phase-12-load.json. Figures are sandbox evidence, not a carrier SLA.
"""

from __future__ import annotations

import json
import os
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "phase-12-load.json"
BUDGETS = json.loads((ROOT / "public" / "sre-budgets.json").read_text(encoding="utf-8"))
CFG = json.loads((ROOT / "public" / "api" / "v1" / "pack" / "config.json").read_text(encoding="utf-8"))
KEY = CFG["demo_api_key"]


def one(base: str, i: int) -> tuple[int, float]:
    body = json.dumps(
        {"area": "jlt", "current_rent": 80000, "proposed_rent": 80000, "n": i}
    ).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/api/v1/tools/lookup_rera_band",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + KEY,
            "Accept": "application/json",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            res.read()
            status = res.status
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            exc.read()
        except Exception:
            pass
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return status, elapsed_ms


def main() -> None:
    base = os.environ.get("HAQQLINE_API_BASE", "http://127.0.0.1:8787").rstrip("/")
    workers = int(os.environ.get("HAQQLINE_LOAD_WORKERS", "8"))
    total = int(os.environ.get("HAQQLINE_LOAD_REQUESTS", "40"))
    target_rps = float(BUDGETS.get("load", {}).get("api_rps_sandbox", {}).get("target", 10))
    success_min = float(BUDGETS.get("load", {}).get("success_rate_min", {}).get("target", 0.95))

    t0 = time.perf_counter()
    results: list[tuple[int, float]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(one, base, i) for i in range(total)]
        for fut in as_completed(futs):
            results.append(fut.result())
    wall_s = time.perf_counter() - t0
    statuses = [s for s, _ in results]
    latencies = [ms for _, ms in results]
    ok = sum(1 for s in statuses if s == 200)
    success_rate = ok / len(results) if results else 0.0
    rps = len(results) / wall_s if wall_s > 0 else 0.0
    latencies_sorted = sorted(latencies)
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95) - 1] if len(latencies_sorted) >= 2 else latencies_sorted[-1]
    p50 = statistics.median(latencies)
    meets = success_rate >= success_min and rps >= target_rps * 0.5  # half target floor for local/CI
    artifact = {
        "phase": 12,
        "environment": "sandbox",
        "label": "Sandbox load sample — not UAE production scale",
        "base": base,
        "workers": workers,
        "requests": total,
        "wall_s": round(wall_s, 3),
        "rps": round(rps, 2),
        "success_rate": round(success_rate, 4),
        "p50_ms": round(float(p50), 1),
        "p95_ms": round(float(p95), 1),
        "status_counts": {str(s): statuses.count(s) for s in sorted(set(statuses))},
        "budgets": {
            "api_rps_sandbox_target": target_rps,
            "success_rate_min": success_min,
        },
        "meets_sandbox_gate": meets,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    if not meets:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
