"""momo 首頁 — 搜尋功能進入點（輸入框、搜尋按鈕、自動完成）。

首頁為新版 UI，搜尋元件帶 data-testid，優先採用；自動完成下拉無 testid，
改用結構選擇器。
"""

from __future__ import annotations

from typing import Self

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config.settings import settings
from pages.base_page import BasePage
from pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    SEARCH_INPUT = '[data-testid="header-search-input"]'
    SEARCH_BUTTON = '[data-testid="header-search-button"]'
    SUGGESTION_DROPDOWN = '[class*="mu-z-dropdown"]'
    SUGGESTION_ITEMS = '[class*="mu-z-dropdown"] button'
    AD_OVERLAY = '[data-testid="ad-overlay"]'
    AD_CLOSE_BUTTON = '[data-testid="close-button-container"]'

    def open_home(self) -> Self:
        self.open(settings.BASE_URL)
        self.dismiss_first_visit_ad()
        return self

    def dismiss_first_visit_ad(self) -> None:
        """首次造訪會延遲跳出全螢幕廣告遮罩並攔截點擊；主動點關閉鈕關掉它。

        遮罩為延遲彈出，故等關閉鈕可點再點；若一直沒出現（非首次造訪）則略過。
        """
        try:
            self.page.locator(self.AD_CLOSE_BUTTON).click(timeout=5000)
            self.page.locator(self.AD_OVERLAY).wait_for(state="hidden", timeout=5000)
        except PlaywrightTimeoutError:
            pass  # 沒有廣告就略過

    # --- 輸入框 ---
    def type_keyword(self, text: str) -> Self:
        """清空後逐字輸入關鍵字，確保觸發前端事件（自動完成需要真實鍵盤輸入）。"""
        box = self.page.locator(self.SEARCH_INPUT)
        box.click()
        box.fill("")
        box.press_sequentially(text, delay=50)
        return self

    def get_input_value(self) -> str:
        return self.page.locator(self.SEARCH_INPUT).input_value()

    def clear_input(self) -> Self:
        """以鍵盤全選後刪除，確保觸發前端事件、讓自動完成收合。"""
        box = self.page.locator(self.SEARCH_INPUT)
        box.click()
        box.press("Control+a")
        box.press("Delete")
        return self

    # --- 送出 ---
    def submit_by_enter(self) -> SearchResultsPage:
        self.page.locator(self.SEARCH_INPUT).press("Enter")
        return SearchResultsPage(self.page).wait_until_loaded()

    def click_search(self) -> SearchResultsPage:
        self.page.locator(self.SEARCH_BUTTON).click()
        return SearchResultsPage(self.page).wait_until_loaded()

    def search(self, keyword: str) -> SearchResultsPage:
        """輸入關鍵字並按搜尋鈕，回傳結果頁。"""
        return self.type_keyword(keyword).click_search()

    def is_search_button_ready(self) -> bool:
        btn = self.page.locator(self.SEARCH_BUTTON)
        btn.wait_for(state="visible")  # 可見即返回，故下方只需再確認是否可點
        return btn.is_enabled()

    # --- 自動完成 ---
    def is_suggestion_visible(self) -> bool:
        try:
            self.page.locator(self.SUGGESTION_DROPDOWN).wait_for(state="visible")
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_suggestions_hidden(self, timeout: int = 5000) -> bool:
        """等待自動完成下拉消失（給清空輸入等情境用，避免可見性逾時的長等待）。"""
        try:
            self.page.locator(self.SUGGESTION_DROPDOWN).wait_for(state="hidden", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def suggestions(self) -> list[str]:
        items = self.page.locator(self.SUGGESTION_ITEMS)
        items.first.wait_for()
        return [t.strip() for t in items.all_inner_texts() if t.strip()]

    def click_suggestion(self, index: int = 0) -> SearchResultsPage:
        self.page.locator(self.SUGGESTION_ITEMS).nth(index).click()
        return SearchResultsPage(self.page).wait_until_loaded()
