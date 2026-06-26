"""momo 搜尋功能 smoke 測試（暫時）。

正式測試案例（IN/BT/AC/SO/PF）後續依 docs/test_cases.md 補上，
此處先放一條串接 HomePage → SearchResultsPage 的 happy path。
"""
import pytest


@pytest.mark.smoke
def test_search_returns_relevant_results(home_page):
    """以常見關鍵字搜尋應回傳結果，且結果與關鍵字相關。"""
    keyword = "筆電"
    results = home_page.type_keyword(keyword).click_search()

    titles = results.product_titles()
    assert titles, "搜尋常見關鍵字卻沒有任何結果"
    assert any(keyword in t for t in titles), "搜尋結果標題與關鍵字不相關"
