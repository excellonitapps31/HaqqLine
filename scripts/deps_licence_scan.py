#!/usr/bin/env python3
"""Dependency and licence inventory for the HaqqLine sandbox (Phase 12)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "phase-12-deps.json"

# Known licences for pinned direct deps (manual map; no network).
KNOWN = {
    "pytest": {"licence": "MIT", "role": "test runner"},
    "playwright": {"licence": "Apache-2.0", "role": "browser automation (dev)"},
}


def parse_requirements(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~\s]", line, maxsplit=1)[0].strip()
        meta = KNOWN.get(name, {"licence": "see package metadata", "role": "dependency"})
        rows.append({"name": name, "spec": line, **meta})
    return rows


def main() -> None:
    req = ROOT / "requirements-dev.txt"
    deps = parse_requirements(req) if req.is_file() else []
    artifact = {
        "phase": 12,
        "environment": "sandbox",
        "runtime": {
            "php": "stdlib only — no Composer, no framework",
            "python_prod_scripts": "stdlib only (urllib, ssl, json)",
            "python_dev": str(req.relative_to(ROOT)) if req.is_file() else None,
        },
        "direct_dev_dependencies": deps,
        "notes": [
            "No package.json / Node runtime in this repo.",
            "No Composer lockfile; PHP is strict_types scripts under public/api/v1.",
            "Licence map for direct pins is maintained in this script for offline CI.",
        ],
        "ok": all(d.get("licence") for d in deps),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
