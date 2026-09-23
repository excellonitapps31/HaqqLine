"""Phase 5 multi-run agent test scaffolding (no network)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_elevenlabs", ROOT / "scripts/sync_elevenlabs.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_default_repeat_count_is_above_one(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.delenv("HAQQLINE_TEST_REPEAT_COUNT", raising=False)
    assert sync.repeat_count() >= 2
    assert sync.repeat_count() == 3


def test_repeat_count_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    sync = load_sync()
    monkeypatch.setenv("HAQQLINE_TEST_REPEAT_COUNT", "2")
    assert sync.repeat_count() == 2
    monkeypatch.setenv("HAQQLINE_TEST_REPEAT_COUNT", "0")
    with pytest.raises(SystemExit):
        sync.repeat_count()
