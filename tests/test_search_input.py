"""搜尋輸入框測試（對應 test_cases.md 之 IN-01 ~ IN-04）。"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)


@pytest.mark.smoke
@pytest.mark.parametrize("keyword", ["iphone", "筆電"], ids=["english", "chinese"])
def test_in01_in02_type_keyword(home_page: HomePage, keyword: str) -> None:
    """IN-01 / IN-02：輸入英文 / 中文關鍵字，文字正確顯示在搜尋框內。"""
    home_page.type_keyword(keyword)
    actual = home_page.get_input_value()
    log.debug("輸入關鍵字=%r 搜尋框顯示=%r", keyword, actual)
    assert actual == keyword


def test_in03_submit_by_enter(home_page: HomePage) -> None:
    """IN-03：以 Enter 鍵送出，等同按搜尋並導向結果頁。"""
    results = home_page.type_keyword("筆電").submit_by_enter()
    titles = results.product_titles()
    log.debug("按 Enter 後結果筆數=%d", len(titles))
    assert titles, "按 Enter 後未導向有結果的搜尋頁"


def test_in04_keyword_retained_after_search(home_page: HomePage) -> None:
    """IN-04：搜尋後關鍵字保留在結果頁的搜尋框內。"""
    keyword = "手機"
    results = home_page.type_keyword(keyword).click_search()
    retained = results.get_keyword_in_box()
    log.debug("搜尋關鍵字=%r 結果頁搜尋框=%r", keyword, retained)
    assert retained == keyword
