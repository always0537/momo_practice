"""排序測試（對應 test_cases.md 之 SO-01 ~ SO-04）。

斷言僅針對非廣告商品（products() 預設已過濾 .sponsor-tag）。
價格與評價排序採同一套處理：方向不靠點擊次數推斷，而是讀取 UI 標示的排序方向
（price/rating_sort_direction），點擊排序直到 UI 顯示目標方向，再驗證實際資料順序與該方向一致。
"""
from typing import Callable

import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)

KEYWORD = "筆電"


def _click_until_direction(
    sort_action: Callable[[], object],
    read_direction: Callable[[], str | None],
    target: str,
    max_clicks: int = 3,
) -> None:
    """點擊排序，直到 UI 標示的方向 == target（以 UI 為準，非靠點擊次數）。"""
    for _ in range(max_clicks):
        sort_action()
        if read_direction() == target:
            return
    raise AssertionError(f"點擊 {max_clicks} 次仍無法切到 {target} 方向（UI 現為 {read_direction()!r}）")


def _assert_order_matches(direction: str, values: list, label: str) -> None:
    """斷言實際資料順序與指定方向一致。"""
    assert len(values) >= 2, f"{label}：結果不足以驗證排序"
    reverse = direction == "desc"
    assert values == sorted(values, reverse=reverse), \
        f"{label}：UI 標示 {direction} 但實際順序不符：{values}"


@pytest.mark.parametrize("direction", ["desc", "asc"], ids=["so01_price_desc", "so02_price_asc"])
def test_sort_by_price(home_page: HomePage, direction: str) -> None:
    """SO-01 / SO-02：點「價格」排序，UI 標示高→低(desc)時價格遞減、低→高(asc)時遞增。"""
    results: SearchResultsPage = home_page.search(KEYWORD)
    _click_until_direction(results.sort_by_price, results.price_sort_direction, direction)
    prices = [p.price() for p in results.products() if p.price() is not None]
    log.debug("價格排序 UI 方向=%s 價格序列=%s", direction, prices)
    _assert_order_matches(direction, prices, "價格排序")


@pytest.mark.parametrize("direction", ["desc", "asc"], ids=["so03_rating_desc", "so04_rating_asc"])
def test_sort_by_rating(home_page: HomePage, direction: str) -> None:
    """SO-03 / SO-04：點「評價」依星等排序，UI 標示高→低(desc)時星等遞減、低→高(asc)時遞增。

    momo「評價」排序的鍵是商品星等（非評價數量），故僅驗星等順序。
    """
    results: SearchResultsPage = home_page.search(KEYWORD)
    _click_until_direction(results.sort_by_rating, results.rating_sort_direction, direction)
    ratings = [p.rating() for p in results.products()]
    log.debug("評價排序 UI 方向=%s 星等序列=%s", direction, ratings)
    _assert_order_matches(direction, ratings, "評價排序")
