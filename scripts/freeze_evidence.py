#!/usr/bin/env python3
"""Phase 13 — export and verify the programme evidence freeze.

No behaviour change. Hashes committed artefacts, records pass rates and
recording/transcript anchors, writes reports/phase-13-evidence.json.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "phase-13-evidence.json"

# Paths relative to repo root. Missing file fails the freeze.
REQUIRED = [
    "README.md",
    "IMPLEMENTATION_PLAN.md",
    "docs/ARCHITECTURE.md",
    "stage-1/ElevenLabs_Idea_Canvas.docx",
    "stage-1/haqqline-architecture-banner.png",
    "stage-1/SOURCES.md",
    "stage-2/BUILD_PLAN.md",
    "stage-2/PRODUCT_SHAPE.md",
    "stage-3/BUILD_PLAN.md",
    "elevenlabs/tests.json",
    "public/sre-budgets.json",
    "reports/phase-04.md",
    "reports/phase-05.md",
    "reports/phase-06.md",
    "reports/phase-07.md",
    "reports/phase-08.md",
    "reports/phase-09.md",
    "reports/phase-10.md",
    "reports/phase-11.md",
    "reports/phase-12.md",
    "reports/phase-13-paths.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_pass_rate(phase04: str) -> dict:
    m = re.search(r"(\d+)\s*/\s*(\d+)\s+passed", phase04)
    if not m:
        raise SystemExit("phase-04.md missing passed/total figure")
    passed, total = int(m.group(1)), int(m.group(2))
    suite = None
    sm = re.search(r"suite_[a-z0-9]+", phase04)
    if sm:
        suite = sm.group(0)
    return {
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "invocation_id": suite,
        "source": "reports/phase-04.md",
        "recorded": "2026-09-22",
    }


def main() -> int:
    artefacts = []
    missing = []
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        artefacts.append(
            {
                "path": rel,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    if missing:
        print("freeze_evidence: missing required artefacts:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    phase04 = (ROOT / "reports/phase-04.md").read_text(encoding="utf-8")
    paths_md = (ROOT / "reports/phase-13-paths.md").read_text(encoding="utf-8")
    tests = json.loads((ROOT / "elevenlabs/tests.json").read_text(encoding="utf-8"))
    names = [t.get("name") for t in tests if isinstance(t, dict)]

    for required_name in (
        "haqqline-sim-en-jlt-within",
        "haqqline-sim-ar-jlt-within",
        "haqqline-sim-en-will-i-win",
        "haqqline-tool-no-unconfirmed-submit",
    ):
        if required_name not in names:
            print(f"freeze_evidence: gold path missing: {required_name}", file=sys.stderr)
            return 1

    if "https://youtu.be/ci3NsthWO0o" not in paths_md:
        print("freeze_evidence: walkthrough URL missing from phase-13-paths.md", file=sys.stderr)
        return 1

    payload = {
        "phase": 13,
        "label": "Programme evidence freeze — Stage 1–3 artefacts already live",
        "frozen_at": "2026-09-23",
        "environment": "sandbox",
        "host": "https://haqqline.excellonit.net",
        "walkthrough_recording": "https://youtu.be/ci3NsthWO0o",
        "architecture_one_pager": "docs/ARCHITECTURE.md",
        "architecture_banner": "stage-1/haqqline-architecture-banner.png",
        "path_evidence": "reports/phase-13-paths.md",
        "pass_rate": extract_pass_rate(phase04),
        "gold_paths": {
            "primary_en": "haqqline-sim-en-jlt-within",
            "primary_ar": "haqqline-sim-ar-jlt-within",
            "failure_advice": "haqqline-sim-en-will-i-win",
            "failure_unconfirmed_submit": "haqqline-tool-no-unconfirmed-submit",
        },
        "residuals_accepted": [
            "phase-05:inbound DID deferred",
            "phase-10:WABA deferred",
            "phase-11:Twilio SMS deferred",
        ],
        "artefacts": artefacts,
        "ok": True,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(artefacts)} artefacts, pass_rate={payload['pass_rate']['pass_rate']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
