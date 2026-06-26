"""根層級 pytest fixtures。"""
import pytest

from pages.home_page import HomePage
from utils.driver_factory import create_driver


@pytest.fixture
def driver():
    """每個測試一個全新的 WebDriver，結束後確實關閉，避免狀態殘留與資源洩漏。"""
    drv = create_driver()
    yield drv
    drv.quit()


@pytest.fixture
def home_page(driver) -> HomePage:
    """已開啟 momo 首頁的 HomePage。"""
    return HomePage(driver).open_home()
