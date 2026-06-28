"""根層級 pytest fixtures（Playwright）。

採用 function-scoped context：每條測試開全新的瀏覽器 context，天然隔離 cookie /
storage，免去 Selenium 版需手動清狀態的 reset 步驟；瀏覽器本身則 session 共用以加速。
"""
import re
from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from config.settings import settings
from pages.home_page import HomePage
from utils.browser_factory import launch_browser, new_context

REPORTS_DIR = Path(__file__).parent / "reports"


@pytest.fixture(scope="session")
def playwright() -> Iterator[Playwright]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Iterator[Browser]:
    """整個測試 session 共用一顆瀏覽器，結束後關閉。"""
    drv = launch_browser(playwright)
    yield drv
    drv.close()


@pytest.fixture
def page(browser: Browser, request: pytest.FixtureRequest) -> Iterator[Page]:
    """每條測試一個全新 context / page；測試失敗時自動截圖到 reports/。"""
    context = new_context(browser)
    pg = context.new_page()
    pg.set_default_timeout(settings.DEFAULT_TIMEOUT_MS)
    pg.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT_MS)
    yield pg
    # setup 與 call 任一階段失敗都截圖：setup 失敗（如 open_home 導頁失敗）正是最需要佐證的情況
    failed = any(
        getattr(getattr(request.node, f"rep_{when}", None), "failed", False)
        for when in ("setup", "call")
    )
    if failed:
        safe_name = re.sub(r"[^\w.-]", "_", request.node.name)
        try:
            pg.screenshot(path=str(REPORTS_DIR / f"{safe_name}.png"), full_page=True)
        except Exception:  # 截圖失敗不應掩蓋原始錯誤
            pass
    context.close()


@pytest.fixture
def home_page(page: Page) -> HomePage:
    """已位於 momo 首頁且狀態乾淨的 HomePage（已關閉開屏廣告）。"""
    return HomePage(page).open_home()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # type: ignore[no-untyped-def]
    """把各階段測試結果掛回 item，供 page fixture 判斷是否需要失敗截圖。"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
