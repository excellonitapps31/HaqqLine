"""Phase 13 evidence freeze: no behaviour change; artefacts hashed and complete."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))


def test_health_phase_at_least_13() -> None:
    assert HEALTH["phase"] >= 13
    assert (ROOT / "docs/ARCHITECTURE.md").is_file()
    assert (ROOT / "reports/phase-13-paths.md").is_file()
    assert (ROOT / "scripts/freeze_evidence.py").is_file()


def test_freeze_evidence_artifact() -> None:
    subprocess.check_call(["python3", str(ROOT / "scripts/freeze_evidence.py")], cwd=str(ROOT))
    art = json.loads((ROOT / "reports/phase-13-evidence.json").read_text(encoding="utf-8"))
    assert art["ok"] is True
    assert art["phase"] == 13
    assert art["pass_rate"]["passed"] == 13
    assert art["pass_rate"]["total"] == 13
    assert art["pass_rate"]["pass_rate"] == 1.0
    assert art["walkthrough_recording"].startswith("https://youtu.be/")
    assert art["architecture_one_pager"] == "docs/ARCHITECTURE.md"
    paths = {a["path"] for a in art["artefacts"]}
    assert "README.md" in paths
    assert "docs/ARCHITECTURE.md" in paths
    assert "elevenlabs/tests.json" in paths
    assert "reports/phase-12.md" in paths
    # Hashes must be stable re-run (same tree → same digest)
    again = json.loads((ROOT / "reports/phase-13-evidence.json").read_text(encoding="utf-8"))
    subprocess.check_call(["python3", str(ROOT / "scripts/freeze_evidence.py")], cwd=str(ROOT))
    rerun = json.loads((ROOT / "reports/phase-13-evidence.json").read_text(encoding="utf-8"))
    by_path = {a["path"]: a["sha256"] for a in again["artefacts"]}
    for a in rerun["artefacts"]:
        assert by_path[a["path"]] == a["sha256"]


def test_architecture_one_pager_content() -> None:
    text = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "HaqqLine" in text
    assert "ExcellonIT" in text
    assert "sandbox" in text.lower()
    assert "HaqqLinePolicy" in text
    assert "youtu.be/ci3NsthWO0o" in text


def test_path_evidence_covers_primary_and_failure() -> None:
    text = (ROOT / "reports/phase-13-paths.md").read_text(encoding="utf-8")
    assert "haqqline-sim-en-jlt-within" in text
    assert "haqqline-sim-ar-jlt-within" in text
    assert "haqqline-sim-en-will-i-win" in text
    assert "haqqline-tool-no-unconfirmed-submit" in text
    assert "13/13" in text


def test_freeze_does_not_alter_pack_lock() -> None:
    """Evidence export must not touch the signed pack (no behaviour change)."""
    before = (ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8")
    subprocess.check_call(["python3", str(ROOT / "scripts/freeze_evidence.py")], cwd=str(ROOT))
    after = (ROOT / "public/api/v1/pack/config.json").read_text(encoding="utf-8")
    assert before == after
    subprocess.check_call(["python3", str(ROOT / "scripts/verify_pack_lock.py")], cwd=str(ROOT))
