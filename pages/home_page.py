"""momo 首頁 — 搜尋功能進入點（輸入框、搜尋按鈕、自動完成）。

首頁為新版 UI，搜尋元件帶 data-testid，優先採用；自動完成下拉無 testid，
改用結構選擇器。
"""

from __future__ import annotations

from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from pages.base_page import BasePage, Locator
from pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    SEARCH_INPUT: Locator = (By.CSS_SELECTOR, '[data-testid="header-search-input"]')
    SEARCH_BUTTON: Locator = (By.CSS_SELECTOR, '[data-testid="header-search-button"]')
    SUGGESTION_DROPDOWN: Locator = (By.CSS_SELECTOR, '[class*="mu-z-dropdown"]')
    SUGGESTION_ITEMS: Locator = (By.CSS_SELECTOR, '[class*="mu-z-dropdown"] button')
    AD_OVERLAY: Locator = (By.CSS_SELECTOR, '[data-testid="ad-overlay"]')
    AD_CLOSE_BUTTON: Locator = (By.CSS_SELECTOR, '[data-testid="close-button-container"]')

    def open_home(self) -> Self:
        self.open(settings.BASE_URL)
        self.dismiss_first_visit_ad()
        return self

    def dismiss_first_visit_ad(self) -> None:
        """首次造訪會延遲跳出全螢幕廣告遮罩並攔截點擊；主動點關閉鈕關掉它。

        遮罩為延遲彈出，故等關閉鈕可點再點；若一直沒出現（非首次造訪）則略過。
        """
        try:
            self.click(self.AD_CLOSE_BUTTON, timeout=5)
            self.wait_invisible(self.AD_OVERLAY, timeout=5)
        except TimeoutException:
            pass  # 沒有廣告就略過

    # --- 輸入框 ---
    def type_keyword(self, text: str) -> Self:
        self.type_text(self.SEARCH_INPUT, text)
        return self

    def get_input_value(self) -> str:
        return self.find(self.SEARCH_INPUT).get_attribute("value") or ""

    def clear_input(self) -> Self:
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

    def search(self, keyword: str) -> SearchResultsPage:
        """輸入關鍵字並按搜尋鈕，回傳結果頁。"""
        return self.type_keyword(keyword).click_search()

    def is_search_button_ready(self) -> bool:
        btn = self.find(self.SEARCH_BUTTON)
        return btn.is_displayed() and btn.is_enabled()

    # --- 自動完成 ---
    def is_suggestion_visible(self) -> bool:
        return self.is_visible(self.SUGGESTION_DROPDOWN)

    def wait_suggestions_hidden(self, timeout: int = 5) -> bool:
        """等待自動完成下拉消失（給清空輸入等情境用，避免可見性逾時的長等待）。"""
        return self.wait_invisible(self.SUGGESTION_DROPDOWN, timeout)

    def suggestions(self) -> list[str]:
        return [e.text.strip() for e in self.find_all(self.SUGGESTION_ITEMS) if e.text.strip()]

    def click_suggestion(self, index: int = 0) -> SearchResultsPage:
        self.find_all(self.SUGGESTION_ITEMS)[index].click()
        return SearchResultsPage(self.driver)
