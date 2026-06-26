"""momo 搜尋功能測試。

骨架階段：先放一個最基本的 happy-path 範例，
後續再依「測試策略」補上邊界 / 異常 / 排序等情境。
"""
import pytest


@pytest.mark.smoke
def test_search_returns_relevant_results(home_page):
    """以常見關鍵字搜尋應回傳結果，且結果與關鍵字相關。"""
    keyword = "iphone"
    results = home_page.search(keyword)

    assert results.has_results(), "搜尋常見關鍵字卻沒有任何結果"
    titles = results.result_titles()
    assert any(keyword.lower() in t.lower() for t in titles), (
        "搜尋結果標題與關鍵字不相關"
    )
