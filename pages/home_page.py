"""momo 首頁 — 搜尋功能進入點（輸入框、搜尋按鈕、自動完成）。

首頁為新版 UI，搜尋元件帶 data-testid，優先採用；自動完成下拉無 testid，
改用結構選擇器。
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from pages.base_page import BasePage
from pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, '[data-testid="header-search-input"]')
    SEARCH_BUTTON = (By.CSS_SELECTOR, '[data-testid="header-search-button"]')
    SUGGESTION_DROPDOWN = (By.CSS_SELECTOR, '[class*="mu-z-dropdown"]')
    SUGGESTION_ITEMS = (By.CSS_SELECTOR, '[class*="mu-z-dropdown"] button')
    AD_OVERLAY = (By.CSS_SELECTOR, '[data-testid="ad-overlay"]')

    def open_home(self) -> "HomePage":
        self.open(settings.BASE_URL)
        self._dismiss_first_visit_ad()
        return self

    def _dismiss_first_visit_ad(self) -> None:
        """首次造訪會延遲跳出全螢幕廣告遮罩並攔截點擊，數秒後自行消失。

        遮罩是延遲彈出的，故先等它出現、再等它消失；若一直沒出現則略過。
        TODO: 暫以「等待遮罩自行消失」繞過，之後改為主動關閉以縮短等待。
        """
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.AD_OVERLAY)
            )
        except Exception:
            return  # 沒有遮罩就直接繼續
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(self.AD_OVERLAY)
            )
        except Exception:
            pass

    # --- 輸入框 ---
    def type_keyword(self, text: str) -> "HomePage":
        self.type_text(self.SEARCH_INPUT, text)
        return self

    def get_input_value(self) -> str:
        return self.find(self.SEARCH_INPUT).get_attribute("value")

    def clear_input(self) -> "HomePage":
        """以鍵盤全選後刪除，確保觸發前端事件、讓自動完成收合。"""
        box = self.find(self.SEARCH_INPUT)
        box.send_keys(Keys.CONTROL, "a")
        box.send_keys(Keys.DELETE)
        return self

    # --- 送出 ---
    def submit_by_enter(self) -> SearchResultsPage:
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)
        return SearchResultsPage(self.driver)

    def click_search(self) -> SearchResultsPage:
        self.click(self.SEARCH_BUTTON)
        return SearchResultsPage(self.driver)

    def is_search_button_ready(self) -> bool:
        btn = self.find(self.SEARCH_BUTTON)
        return btn.is_displayed() and btn.is_enabled()

    # --- 自動完成 ---
    def is_suggestion_visible(self) -> bool:
        return self.is_visible(self.SUGGESTION_DROPDOWN)

    def suggestions(self) -> list[str]:
        return [e.text.strip() for e in self.find_all(self.SUGGESTION_ITEMS) if e.text.strip()]

    def click_suggestion(self, index: int = 0) -> SearchResultsPage:
        self.find_all(self.SUGGESTION_ITEMS)[index].click()
        return SearchResultsPage(self.driver)
