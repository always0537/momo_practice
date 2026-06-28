"""單張搜尋結果商品卡片（component）。

封裝在 `li.listAreaLi` 元素之上，提供排序 / 篩選斷言所需的取值：
價格、評分、評價數、是否為廣告卡。由 `SearchResultsPage.products()` 產生。

為降低 Playwright 逐元素往返的成本，建構後以一次 `evaluate` 取回整張卡片的原始資料快照
（標題 / 價格文字 / 星等 path / 是否廣告），數值解析仍留在 Python 端。
"""
from __future__ import annotations

import re

from playwright.sync_api import Locator


class ProductCard:
    # momo 實心 / 半 / 空心星「都會渲染」，且實心與空心**共用同一 path 前綴 (m20.547)、
    # fill 也同色**，差別在：空心星的 path 多一段「內凹子路徑」把星星中心挖空成輪廓。
    # 因此實心 vs 空心要看子路徑 (moveto) 段數——實心=1 段、空心=2 段；半星則為獨立 path
    # (前綴 M21.151)。只比對前綴或 fill 會把空心星誤判為滿星，務必用段數判斷。
    _HALF_STAR_PREFIX: str = "M21.151"
    _MOVETO = re.compile(r"[Mm]")

    def __init__(self, root: Locator) -> None:
        self.root: Locator = root
        self._data: dict | None = None

    def _snapshot(self) -> dict:
        """一次往返取回整張卡片所需的原始資料（lazy，取一次後快取）。"""
        if self._data is None:
            self._data = self.root.evaluate(
                """el => {
                    const text = s => { const n = el.querySelector(s); return n ? n.textContent.trim() : null; };
                    const starPaths = [...el.querySelectorAll('.ratingStars svg')].map(svg => {
                        const p = svg.querySelector('path');
                        return p ? (p.getAttribute('d') || '') : '';
                    });
                    return {
                        title: text('a.prdName'),
                        price: text('.price'),
                        starPaths,
                        isAd: !!el.querySelector('.sponsor-tag'),
                    };
                }"""
            )
        return self._data

    @property
    def title(self) -> str | None:
        return self._snapshot()["title"]

    def price(self) -> int | None:
        """價格數值，去除 `$` 與千分位逗號後轉為 int。"""
        raw = self._snapshot()["price"]
        digits = re.sub(r"[^\d]", "", raw) if raw else ""
        return int(digits) if digits else None

    def rating(self) -> float:
        """評分 = 實心星數 + 0.5 × 半星數（空心星不計）。"""
        full = half = 0
        for d in self._snapshot()["starPaths"]:
            if not d:
                continue
            if d.startswith(self._HALF_STAR_PREFIX):
                half += 1
            elif len(self._MOVETO.findall(d)) == 1:  # 單一子路徑 = 實心滿星
                full += 1
            # 其餘為空心星（多一段內凹子路徑），不計
        return full + 0.5 * half

    def is_ad(self) -> bool:
        return self._snapshot()["isAd"]
