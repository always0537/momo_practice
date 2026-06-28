"""搜尋按鈕測試（對應 test_cases.md 之 BT-01 ~ BT-02）。"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)

# 真實電商搜尋含模糊比對 / 配件組合，少數結果標題未必含關鍵字；
# 故以「多數結果相關」為準，而非要求每一筆都含關鍵字（後者對 live 站台過於脆弱）。
RELEVANCE_THRESHOLD = 0.7


@pytest.mark.smoke
def test_bt01_search_button_ready(home_page: HomePage) -> None:
    """BT-01：搜尋按鈕顯示且可點擊。"""
    ready = home_page.is_search_button_ready()
    log.debug("搜尋按鈕可用=%s", ready)
    assert ready


@pytest.mark.smoke
def test_bt02_click_search_returns_relevant_results(home_page: HomePage) -> None:
    """BT-02：有關鍵字時點擊搜尋，導向結果頁且多數結果與關鍵字相關。"""
    keyword = "滑鼠"
    results = home_page.type_keyword(keyword).click_search()
    titles = results.product_titles()
    assert titles, "點擊搜尋後沒有任何結果"
    ratio = sum(keyword in t for t in titles) / len(titles)
    log.debug("關鍵字=%r 結果筆數=%d 相關比例=%.0f%% 前三筆=%s", keyword, len(titles), ratio * 100, titles[:3])
    assert ratio >= RELEVANCE_THRESHOLD, (
        f"相關結果比例 {ratio:.0%} 低於門檻 {RELEVANCE_THRESHOLD:.0%}；"
        f"未含關鍵字者：{[t for t in titles if keyword not in t]}"
    )
