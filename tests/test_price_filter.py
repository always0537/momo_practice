"""價格區間篩選測試（對應 test_cases.md 之 PF-01 ~ PF-03）。

斷言僅針對非廣告商品（products() 預設已過濾 .sponsor-tag）。
"""
import pytest

from pages.home_page import HomePage
from utils.logger import get_logger

pytestmark = pytest.mark.search

log = get_logger(__name__)

KEYWORD = "滑鼠"


@pytest.mark.parametrize(
    "low, high",
    [(300, 800), (500, None), (None, 600)],
    ids=["range", "min_only", "max_only"],
)
def test_pf01_pf02_pf03_price_filter(
    home_page: HomePage, low: int | None, high: int | None
) -> None:
    """PF-01 / PF-02 / PF-03：套用價格區間（含只設單邊）後，所有結果價格落在界內。"""
    results = home_page.search(KEYWORD).set_price_range(low, high).apply_price_filter()
    prices = [price for p in results.products() if (price := p.price()) is not None]
    log.debug("篩選區間 min=%s max=%s 結果價格=%s", low, high, prices)
    assert prices, "套用價格篩選後沒有結果"
    if low is not None:
        assert all(p >= low for p in prices), f"有結果低於最低價 {low}：{prices}"
    if high is not None:
        assert all(p <= high for p in prices), f"有結果高於最高價 {high}：{prices}"
