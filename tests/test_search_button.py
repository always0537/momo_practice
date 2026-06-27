"""搜尋按鈕測試（對應 test_cases.md 之 BT-01 ~ BT-02）。"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)


@pytest.mark.smoke
def test_bt01_search_button_ready(home_page: HomePage) -> None:
    """BT-01：搜尋按鈕顯示且可點擊。"""
    ready = home_page.is_search_button_ready()
    log.debug("搜尋按鈕可用=%s", ready)
    assert ready


@pytest.mark.smoke
def test_bt02_click_search_returns_relevant_results(home_page: HomePage) -> None:
    """BT-02：有關鍵字時點擊搜尋，導向結果頁且結果與關鍵字相關。"""
    keyword = "滑鼠"
    results = home_page.type_keyword(keyword).click_search()
    titles = results.product_titles()
    matched = sum(keyword in t for t in titles)
    log.debug("關鍵字=%r 結果筆數=%d 含關鍵字筆數=%d 前三筆=%s", keyword, len(titles), matched, titles[:3])
    assert titles, "點擊搜尋後沒有任何結果"
    unmatched = [t for t in titles if keyword not in t]
    assert all(keyword in t for t in titles), f"有結果與關鍵字不相關：{unmatched}"
