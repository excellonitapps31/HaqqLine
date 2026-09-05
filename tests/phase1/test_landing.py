from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "public" / "app.js").read_text(encoding="utf-8")


def test_disclaimer_visible_in_english_and_arabic() -> None:
    assert "not a government service" in HTML
    assert "ليس خدمة حكومية" in HTML
    assert "Sandbox" in HTML
    assert "بيئة تجريبية" in HTML


def test_affiliation_and_product_identity() -> None:
    assert "HaqqLine" in HTML
    assert "ExcellonIT" in HTML
    assert "DLD" in HTML
    assert "RERA" in HTML
    assert "Rental Disputes Center" in HTML
    assert "JustNow" not in HTML


def test_bilingual_shell_and_honest_scope() -> None:
    assert 'data-lang-switch="en"' in HTML
    assert 'data-lang-switch="ar"' in HTML
    assert 'document.documentElement.dir' in JS
    assert '"rtl"' in JS
    assert "The agent, telephone line, WhatsApp, and SMS are not connected here yet." in HTML
    assert "Try a case" in HTML
    assert "noindex" in HTML


def test_assets_are_self_hosted_paths() -> None:
    assert 'href="/styles.css"' in HTML
    assert 'src="/app.js"' in HTML
    assert 'href="/favicon.svg"' in HTML
