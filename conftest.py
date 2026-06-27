"""根層級 pytest fixtures。"""
from typing import Iterator

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings
from pages.home_page import HomePage
from utils.driver_factory import create_driver


@pytest.fixture(scope="session")
def driver() -> Iterator[WebDriver]:
    """整個測試 session 共用一顆 WebDriver，結束後關閉。"""
    drv = create_driver()
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def reset_browser(driver: WebDriver) -> Iterator[None]:
    """每條測試前重置瀏覽器狀態，確保各測試起點一致、互不影響。

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


@pytest.fixture
def home_page(driver: WebDriver, reset_browser: None) -> HomePage:
    """已位於 momo 首頁且狀態乾淨的 HomePage。"""
    return HomePage(driver)
