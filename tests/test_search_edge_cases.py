"""搜尋邊界 / 負向案例（對應 test_cases.md 之 NR-01、EG-01）。

正向流程之外，驗證兩個行為明確、可穩定斷言的情境：查無結果的空狀態、
關鍵字前後空白被忽略。其餘規則未明的情境（空字串、特殊字元上限等）仍暫不納入。
"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)

# 與正向相關性測試一致的門檻：以「多數結果相關」為準。
RELEVANCE_THRESHOLD = 0.7


def test_nr01_no_results_shows_empty_state(home_page: HomePage) -> None:
    """NR-01：搜尋不存在的關鍵字，顯示『查無結果』空狀態且無任何商品卡。"""
    results = home_page.search("zxqwklmnzzqq9988")
    shown = results.is_no_results_shown()
    count = results.product_count()
    log.debug("查無結果空狀態顯示=%s 商品卡數=%d", shown, count)
    assert shown, "查無結果時未顯示空狀態提示"
    assert count == 0, f"查無結果卻仍出現 {count} 張商品卡片"


def test_eg01_whitespace_is_trimmed(home_page: HomePage) -> None:
    """EG-01：關鍵字前後空白被忽略，搜尋『  滑鼠  』仍回傳與『滑鼠』相關的結果。"""
    keyword = "滑鼠"
    results = home_page.search(f"  {keyword}  ")
    titles = results.product_titles()
    assert titles, "加前後空白搜尋後沒有任何結果"
    ratio = sum(keyword in t for t in titles) / len(titles)
    log.debug("前後空白搜尋 結果筆數=%d 相關比例=%.0f%%", len(titles), ratio * 100)
    assert ratio >= RELEVANCE_THRESHOLD, (
        f"前後空白未被正確處理，相關比例僅 {ratio:.0%}（門檻 {RELEVANCE_THRESHOLD:.0%}）"
    )
