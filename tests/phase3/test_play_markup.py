import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "public/play/index.html").read_text(encoding="utf-8")
JS = (ROOT / "public/play/play.js").read_text(encoding="utf-8")
HEALTH = json.loads((ROOT / "public/health.json").read_text(encoding="utf-8"))


def test_four_gold_scenarios_exist() -> None:
    for key in ("within", "overband", "unknown", "advice"):
        assert f'data-scenario="{key}"' in HTML
        assert f'data-testid="scenario-{key}"' in HTML


def test_filing_gate_and_ledger() -> None:
    assert 'data-testid="file-blocked"' in HTML
    assert 'data-testid="file-confirm"' in HTML
    assert 'data-testid="ledger"' in HTML
    assert "submit_to_human_queue" in JS
    assert "caller_confirmed" in JS
    assert "/api/v1/audit" in JS


def test_no_pii_fields() -> None:
    lowered = HTML.lower()
    assert "<input" not in lowered
    assert 'type="email"' not in lowered
    assert 'type="tel"' not in lowered
    assert "passport" not in lowered
    assert "emirates id" not in lowered
    assert "SCENARIO-" in JS
    assert "not a government service" in HTML
    assert "ليس خدمة حكومية" in HTML
    assert HEALTH["phase"] >= 3
    assert HEALTH["channels"]["playground"] is True
