"""搜尋結果頁 — 提供讓測試斷言用的查詢方法。

注意：以下 Locator 為初版骨架，實際的 selector 需在探索網站後校正。
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    # TODO: 探索網站後確認以下定位子
    RESULT_ITEMS = (By.CSS_SELECTOR, "li.goodsItemLi")
    RESULT_TITLES = (By.CSS_SELECTOR, "li.goodsItemLi p.prdName")
    NO_RESULT_HINT = (By.CSS_SELECTOR, ".noResultArea")
    RESULT_COUNT_TEXT = (By.CSS_SELECTOR, ".totalTxt")

    def result_count(self) -> int:
        """目前結果頁顯示的商品數量。"""
        return len(self.driver.find_elements(*self.RESULT_ITEMS))

    def result_titles(self) -> list[str]:
        """所有商品標題文字，供關鍵字比對使用。"""
        return [e.text for e in self.find_all(self.RESULT_TITLES)]

    def has_results(self) -> bool:
        return self.result_count() > 0

    def is_no_result(self) -> bool:
        """是否顯示『查無結果』提示。"""
        return self.is_visible(self.NO_RESULT_HINT)
