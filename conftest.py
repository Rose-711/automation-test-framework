"""Root-level conftest: shared fixtures for the entire test suite.

NOTE: pytest-playwright provides built-in fixtures:
  playwright, browser, browser_name, context, page, base_url
We override `context` and `page` to use custom settings from .env.
"""
import json
from pathlib import Path
from typing import Dict

import allure
import pytest
import yaml
from playwright.sync_api import Browser, BrowserContext, Page

from config import settings


# ── Test collection hooks ────────────────────────────────────────────────────

def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Deselect slow tests unless --run-slow is given."""
    if config.getoption("--run-slow", default=False):
        return
    skip_slow = pytest.mark.skip(reason="use --run-slow to include")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# ── Override Playwright fixtures with custom settings ────────────────────────

@pytest.fixture(scope="session")
def browser(playwright, browser_name) -> Browser:
    """Launch browser once per session.

    Uses system-installed Chrome when available (channel="chrome"),
    otherwise falls back to Playwright's bundled browser.
    """
    browser_type = getattr(playwright, browser_name)
    launch_kwargs: dict = {
        "headless": settings.HEADLESS,
        "slow_mo": settings.SLOW_MO,
    }
    if browser_name == "chromium":
        launch_kwargs["channel"] = "chrome"  # use system Chrome
        launch_kwargs["args"] = ["--disable-blink-features=AutomationControlled"]
    b = browser_type.launch(**launch_kwargs)
    yield b
    b.close()


@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    """Create an isolated browser context per test."""
    ctx = browser.new_context(
        viewport={"width": settings.VIEWPORT_WIDTH, "height": settings.VIEWPORT_HEIGHT},
        locale=settings.LOCALE,
        timezone_id=settings.TIMEZONE,
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """Create a new page (tab) for each test."""
    p = context.new_page()
    p.set_default_timeout(settings.DEFAULT_TIMEOUT)
    p.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    yield p
    p.close()


# ── Allure integration ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def allure_environment(request: pytest.FixtureRequest) -> None:
    """Attach dynamic feature/story tags to Allure report."""
    parent = request.node.parent
    allure.dynamic.feature(getattr(parent, "name", "Unknown"))
    allure.dynamic.story(request.node.name)


# ── Test data helpers ────────────────────────────────────────────────────────

@pytest.fixture()
def test_data() -> Dict:
    """Load test data from JSON/YAML files in testdata/."""
    data = {}
    for filepath in settings.TESTDATA_DIR.glob("*"):
        if filepath.suffix in (".json",):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = json.load(f)
        elif filepath.suffix in (".yaml", ".yml"):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = yaml.safe_load(f)
    return data


# ── Screenshot on failure ────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Capture a screenshot when a test fails and attach to Allure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_path = settings.SCREENSHOTS_DIR / f"{item.name}_{call.when}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name=f"Failure: {item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
