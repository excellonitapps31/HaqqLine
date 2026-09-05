from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


@pytest.fixture(scope="session")
def play_base() -> str:
    env = os.environ.get("HAQQLINE_PLAY_BASE")
    if env:
        yield env.rstrip("/")
        return
    port = _free_port()
    proc = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}", "-t", str(ROOT / "public"), str(ROOT / "public" / "router.php")],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import urllib.request

    deadline = time.time() + 8
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/health", timeout=0.3)
            break
        except Exception:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("php server failed")
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_gold_paths_and_blocked_submit(play_base: str, browser) -> None:
    context = browser.new_context()
    page = context.new_page()
    page.goto(play_base + "/play/", wait_until="networkidle")
    page.locator('[data-testid="scenario-within"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('permitted_increase_pct')")
    assert "proposed_is_within_band: true" in page.locator('[data-testid="result"]').inner_text()

    page.locator('[data-testid="scenario-overband"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('proposed_is_within_band: false')")

    page.locator('[data-testid="scenario-unknown"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('escalate: true')")
    assert "No index invented" in page.locator('[data-testid="result"]').inner_text()

    page.locator('[data-testid="scenario-advice"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('Advice is not answered')")

    page.locator('[data-testid="file-blocked"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('confirmation_required')")

    page.locator('[data-testid="file-confirm"]').click()
    page.wait_for_function("document.querySelector('[data-testid=result]').innerText.includes('pending_human')")
    assert "SCENARIO-" in page.locator('[data-testid="ledger"]').inner_text() or "submit_to_human_queue" in page.locator('[data-testid="ledger"]').inner_text()

    page.close()
    context.close()


def test_arabic_toggle_a11y(play_base: str, browser) -> None:
    context = browser.new_context()
    page = context.new_page()
    page.goto(play_base + "/play/", wait_until="networkidle")
    page.get_by_role("button", name="العربية").click()
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"
    banner = page.locator(".banner").inner_text()
    assert "خدمة حكومية" in banner
    page.close()
    context.close()
