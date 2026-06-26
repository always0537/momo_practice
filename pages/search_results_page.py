"""搜尋結果頁 — 提供排序、價格篩選與結果取值，供測試斷言。

結果頁為 momo 舊版 UI（無 data-testid），改用 id / class / 結構選擇器。
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from pages.product_card import ProductCard


class SearchResultsPage(BasePage):
    SEARCH_INPUT = (By.ID, "header-search-input")  # 頂部搜尋框（驗關鍵字保留）
    SORT_PRICE = (By.XPATH, "//li[contains(@class,'priceHeight') and normalize-space()='價格']")
    SORT_RATING = (By.XPATH, "//li[contains(@class,'priceHeight') and normalize-space()='評價']")
    MIN_PRICE_INPUT = (By.ID, "priceS")
    MAX_PRICE_INPUT = (By.ID, "priceE")
    CONFIRM_BUTTON = (By.CSS_SELECTOR, "a.priceBtn")
    PRODUCT_CARDS = (By.CSS_SELECTOR, "li.listAreaLi")

    # --- 查詢 ---
    def get_keyword_in_box(self) -> str:
        """讀取結果頁頂部搜尋框現值。"""
        return self.find(self.SEARCH_INPUT).get_attribute("value")

    def products(self, exclude_ads: bool = True) -> list[ProductCard]:
        """回傳結果卡片清單；預設過濾掉廣告卡（`.sponsor-tag`）。"""
        self.find(self.PRODUCT_CARDS)  # 等待至少一張卡片出現
        cards = [ProductCard(el) for el in self.driver.find_elements(*self.PRODUCT_CARDS)]
        return [c for c in cards if not c.is_ad()] if exclude_ads else cards

    def product_titles(self, exclude_ads: bool = True) -> list[str]:
        return [c.title for c in self.products(exclude_ads) if c.title]

    # --- 排序 ---
    def sort_by_price(self) -> "SearchResultsPage":
        """點價格排序（重複呼叫可切換遞增 / 遞減）。"""
        self._refresh_results(lambda: self.click(self.SORT_PRICE))
        return self

    def sort_by_rating(self) -> "SearchResultsPage":
        self._refresh_results(lambda: self.click(self.SORT_RATING))
        return self

    # --- 價格篩選 ---
    def set_price_range(self, min_price: int | None = None, max_price: int | None = None) -> "SearchResultsPage":
        """填入最低 / 最高價；傳 None 則略過該欄。"""
        if min_price is not None:
            self.type_text(self.MIN_PRICE_INPUT, str(min_price))
        if max_price is not None:
            self.type_text(self.MAX_PRICE_INPUT, str(max_price))
        return self

    def apply_price_filter(self) -> "SearchResultsPage":
        """按「確認」套用價格篩選。"""
        self._refresh_results(lambda: self.click(self.CONFIRM_BUTTON))
        return self

    # --- 內部 ---
    def _refresh_results(self, action) -> None:
        """執行會重整結果列表的動作後，等待舊卡片失效並確認新列表載入。"""
        old_cards = self.driver.find_elements(*self.PRODUCT_CARDS)
        action()
        if old_cards:
            try:
                self.wait.until(EC.staleness_of(old_cards[0]))
            except Exception:
                pass  # 若未觸發整頁重載則略過，下一行仍會等待卡片
        self.find(self.PRODUCT_CARDS)
