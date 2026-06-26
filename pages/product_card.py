"""單張搜尋結果商品卡片（component）。

封裝在 `li.listAreaLi` 元素之上，提供排序 / 篩選斷言所需的取值：
價格、評分、評價數、是否為廣告卡。由 `SearchResultsPage.products()` 產生。
"""
from __future__ import annotations

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class ProductCard:
    NAME = (By.CSS_SELECTOR, "a.prdName")
    PRICE = (By.CSS_SELECTOR, ".price")
    REVIEW_COUNT = (By.CSS_SELECTOR, ".ratingCounts .number")
    STARS = (By.CSS_SELECTOR, ".ratingStars svg")
    AD_BADGE = (By.CSS_SELECTOR, ".sponsor-tag")

    # momo 只渲染有填色的星，滿星與半星的 SVG path 幾何不同，藉此區分
    _FULL_STAR_PREFIX = "m20.547"
    _HALF_STAR_PREFIX = "M21.151"

    def __init__(self, element: WebElement):
        self.el = element

    def _text(self, locator) -> str | None:
        found = self.el.find_elements(*locator)
        return found[0].text.strip() if found else None

    @property
    def title(self) -> str | None:
        return self._text(self.NAME)

    def price(self) -> int | None:
        """價格數值，去除 `$` 與千分位逗號後轉為 int。"""
        raw = self._text(self.PRICE)
        digits = re.sub(r"[^\d]", "", raw) if raw else ""
        return int(digits) if digits else None

    def review_count(self) -> int:
        """評價數量，例如 `(168)` → 168；無評價回傳 0。"""
        raw = self._text(self.REVIEW_COUNT)
        digits = re.sub(r"[^\d]", "", raw) if raw else ""
        return int(digits) if digits else 0

    def rating(self) -> float:
        """評分 = 滿星數 + 0.5 × 半星數。"""
        full = half = 0
        for svg in self.el.find_elements(*self.STARS):
            paths = svg.find_elements(By.TAG_NAME, "path")
            d = (paths[0].get_attribute("d") or "") if paths else ""
            if d.startswith(self._FULL_STAR_PREFIX):
                full += 1
            elif d.startswith(self._HALF_STAR_PREFIX):
                half += 1
        return full + 0.5 * half

    def is_ad(self) -> bool:
        return len(self.el.find_elements(*self.AD_BADGE)) > 0
