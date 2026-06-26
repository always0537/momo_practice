"""momo 購物網站首頁 — 搜尋功能的進入點。

注意：以下 Locator 為初版骨架，實際的 selector 需在探索網站後校正。
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from pages.base_page import BasePage
from pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    # TODO: 探索網站後確認以下定位子
    SEARCH_INPUT = (By.ID, "keyword")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button.searchTextBtn")

    def open_home(self) -> "HomePage":
        self.open(settings.BASE_URL)
        return self

    def search(self, keyword: str) -> SearchResultsPage:
        """輸入關鍵字並送出搜尋，回傳搜尋結果頁。"""
        self.type_text(self.SEARCH_INPUT, keyword)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)
        return SearchResultsPage(self.driver)
