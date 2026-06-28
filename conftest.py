"""根層級 pytest fixtures。"""
import re
from pathlib import Path
from typing import Iterator

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings
from pages.home_page import HomePage
from utils.driver_factory import create_driver

REPORTS_DIR = Path(__file__).parent / "reports"


@pytest.fixture(scope="session")
def driver() -> Iterator[WebDriver]:
    """整個測試 session 共用一顆 WebDriver，結束後關閉。"""
    drv = create_driver()
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def reset_browser(driver: WebDriver, request: pytest.FixtureRequest) -> Iterator[None]:
    """每條測試前重置瀏覽器狀態，確保各測試起點一致、互不影響；測試失敗時自動截圖。

    導向首頁 → 清除 cookie / storage → 重整，並關閉首次造訪的開屏廣告。
    （清除 cookie 會使開屏廣告重新出現，故仍需在此關閉。）
    """
    driver.get(settings.BASE_URL)
    driver.delete_all_cookies()
    try:
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    except WebDriverException:
        pass
    driver.refresh()
    HomePage(driver).dismiss_first_visit_ad()
    yield
    # setup 與 call 任一階段失敗都截圖：保留失敗當下畫面佐證（session 共用 driver，
    # 此時頁面仍停在失敗現場，下一條測試的 reset 才會導走）。
    failed = any(
        getattr(getattr(request.node, f"rep_{when}", None), "failed", False)
        for when in ("setup", "call")
    )
    if failed:
        safe_name = re.sub(r"[^\w.-]", "_", request.node.name)
        try:
            REPORTS_DIR.mkdir(exist_ok=True)
            driver.save_screenshot(str(REPORTS_DIR / f"{safe_name}.png"))
        except Exception:  # 截圖失敗不應掩蓋原始錯誤
            pass


@pytest.fixture
def home_page(driver: WebDriver, reset_browser: None) -> HomePage:
    """已位於 momo 首頁且狀態乾淨的 HomePage。"""
    return HomePage(driver)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # type: ignore[no-untyped-def]
    """把各階段測試結果掛回 item，供 reset_browser 判斷是否需要失敗截圖。"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
