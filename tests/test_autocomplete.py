"""自動完成測試（對應 test_cases.md 之 AC-01 ~ AC-04）。"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)


def test_ac01_suggestions_appear(home_page: HomePage) -> None:
    """AC-01：輸入數個字元後出現自動完成下拉建議。"""
    home_page.type_keyword("筆電")
    visible = home_page.is_suggestion_visible()
    log.debug("輸入後建議下拉可見=%s", visible)
    assert visible


def test_ac02_suggestions_relevant(home_page: HomePage) -> None:
    """AC-02：建議內容與輸入關鍵字相關。"""
    keyword = "手機"
    home_page.type_keyword(keyword)
    suggestions = home_page.suggestions()
    log.debug("關鍵字=%r 建議項=%s", keyword, suggestions)
    assert suggestions, "未取得任何建議項"
    irrelevant = [s for s in suggestions if keyword not in s]
    assert all(keyword in s for s in suggestions), f"有建議項與輸入關鍵字不相關：{irrelevant}"


def test_ac03_click_suggestion_triggers_search(home_page: HomePage) -> None:
    """AC-03：點擊建議項後觸發搜尋並導向結果頁。"""
    home_page.type_keyword("筆電")
    assert home_page.is_suggestion_visible()
    results = home_page.click_suggestion(0)
    titles = results.product_titles()
    log.debug("點擊建議項後結果筆數=%d", len(titles))
    assert titles, "點擊建議項後未導向有結果的搜尋頁"


def test_ac04_clear_input_hides_suggestions(home_page: HomePage) -> None:
    """AC-04：清空輸入內容後建議清單消失。"""
    home_page.type_keyword("筆電")
    assert home_page.is_suggestion_visible()
    home_page.clear_input()
    hidden = home_page.wait_suggestions_hidden()
    log.debug("清空輸入後建議下拉消失=%s", hidden)
    assert hidden, "清空輸入後建議清單仍未消失"
