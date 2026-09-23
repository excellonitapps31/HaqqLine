#!/usr/bin/env python3
"""Backup/restore drill for HaqqLine sandbox JSONL stores (Phase 12).

Creates a tar of cases/audit/alerts/sms JSONL, restores into a temp dir,
verifies line counts, writes reports/phase-12-restore.json.
"""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "api" / "data"
REPORT = ROOT / "reports" / "phase-12-restore.json"
PATTERNS = (
    "cases.jsonl",
    "audit.jsonl",
    "alerts.jsonl",
    "queue.jsonl",
    "escalations.jsonl",
    "conversations.jsonl",
    "sms-outbox.jsonl",
    "sms-inbound.jsonl",
    "sms-optout.jsonl",
)


def line_count(path: Path) -> int:
    if not path.is_file() or path.stat().st_size == 0:
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


def collect_sources() -> list[Path]:
    DATA.mkdir(parents=True, exist_ok=True)
    # Ensure at least empty files exist for a deterministic drill.
    for name in PATTERNS:
        path = DATA / name
        if not path.exists():
            path.write_text("", encoding="utf-8")
    return [DATA / name for name in PATTERNS if (DATA / name).is_file()]


def main() -> None:
    t0 = time.perf_counter()
    sources = collect_sources()
    before = {p.name: line_count(p) for p in sources}
    with tempfile.TemporaryDirectory(prefix="haqqline-restore-") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "sandbox-data.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for path in sources:
                tar.add(path, arcname=path.name)
        restore_dir = tmp_path / "restore"
        restore_dir.mkdir()
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(restore_dir)
        after = {p.name: line_count(restore_dir / p.name) for p in sources}
        ok = before == after
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        artifact = {
            "phase": 12,
            "environment": "sandbox",
            "label": "Sandbox restore drill — not a UAE production RPO/RTO commitment",
            "ok": ok,
            "elapsed_ms": elapsed_ms,
            "archive_bytes": archive.stat().st_size,
            "files": before,
            "restored": after,
            "notes": "Drill copies JSONL under public/api/data into a temp restore tree; live host wipe remains operator-controlled.",
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(artifact, indent=2))
        if not ok:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
