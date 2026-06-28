"""搜尋結果頁 — 提供排序、價格篩選與結果取值，供測試斷言。

結果頁為 momo 舊版 UI（無 data-testid），改用 id / class / 結構選擇器。
"""
from __future__ import annotations

import time
from typing import Callable, Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from pages.product_card import ProductCard


class SearchResultsPage(BasePage):
    SEARCH_INPUT: Locator = (By.ID, "header-search-input")  # 頂部搜尋框（驗關鍵字保留）
    SORT_PRICE: Locator = (By.XPATH, "//li[contains(@class,'priceHeight') and normalize-space()='價格']")
    SORT_RATING: Locator = (By.XPATH, "//li[contains(@class,'priceHeight') and normalize-space()='評價']")
    MIN_PRICE_INPUT: Locator = (By.ID, "priceS")
    MAX_PRICE_INPUT: Locator = (By.ID, "priceE")
    CONFIRM_BUTTON: Locator = (By.CSS_SELECTOR, "a.priceBtn")
    PRODUCT_CARDS: Locator = (By.CSS_SELECTOR, "li.listAreaLi")
    NO_RESULTS: Locator = (By.CSS_SELECTOR, ".noSearchResultWrapper")  # 查無結果空狀態容器

    _min_price: int | None = None
    _max_price: int | None = None

    # --- 查詢 ---
    def get_keyword_in_box(self) -> str:
        """讀取結果頁頂部搜尋框現值。"""
        return self.find(self.SEARCH_INPUT).get_attribute("value") or ""

    def products(self, exclude_ads: bool = True) -> list[ProductCard]:
        """回傳結果卡片清單；預設過濾掉廣告卡（`.sponsor-tag`）。"""
        self.find(self.PRODUCT_CARDS)  # 等待至少一張卡片出現
        cards = [ProductCard(el) for el in self.driver.find_elements(*self.PRODUCT_CARDS)]
        return [c for c in cards if not c.is_ad()] if exclude_ads else cards

    def product_titles(self, exclude_ads: bool = True) -> list[str]:
        return [c.title for c in self.products(exclude_ads) if c.title]

    def product_count(self) -> int:
        """目前頁面的商品卡數量（不等待，供『查無結果』情境直接點數）。"""
        return len(self.driver.find_elements(*self.PRODUCT_CARDS))

    def is_no_results_shown(self) -> bool:
        """是否顯示『查無結果』空狀態（搜尋不到符合商品時 momo 會渲染此區塊）。"""
        return self.is_visible(self.NO_RESULTS)

    # --- 排序 ---
    def sort_by_price(self) -> Self:
        """點價格排序（重複呼叫可切換遞增 / 遞減）。"""
        self._refresh_results(lambda: self.click(self.SORT_PRICE))
        return self

    def sort_by_rating(self) -> Self:
        self._refresh_results(lambda: self.click(self.SORT_RATING))
        return self

    def _sort_direction(self, sort_locator: Locator) -> str | None:
        """讀取排序欄目前 UI 標示的方向。

        momo 以排序 li 的 class token 標示：`down`=高→低（遞減）、`up`=低→高（遞增）、
        兩者皆無=未排序。據此讓測試「依 UI 呈現的方向」驗對應排序，而非靠點擊次數推斷。
        """
        classes = (self.find(sort_locator).get_attribute("class") or "").split()
        if "down" in classes:
            return "desc"
        if "up" in classes:
            return "asc"
        return None

    def price_sort_direction(self) -> str | None:
        return self._sort_direction(self.SORT_PRICE)

    def rating_sort_direction(self) -> str | None:
        return self._sort_direction(self.SORT_RATING)

    # --- 價格篩選 ---
    def set_price_range(self, min_price: int | None = None, max_price: int | None = None) -> Self:
        """以真實 UI 操作填入最低 / 最高價；傳 None 則略過該欄。

        momo 結果頁的價格篩選，確認鈕送出的是一個 React 參數物件（內部稱 t /
        menuSearchParameter）。搜尋結果非同步載入期間，上層元件會反覆 re-render，每次都把
        這個物件「重建回預設值」，洗掉剛填入的值——此時 DOM 雖顯示我們打的數字，送出的卻是
        預設值（不導頁 / 篩選未套用）。因此先等該物件穩定（不再被重建）再填值，才會穩定生效。

        注意：這裡讀取 t 僅作為「頁面已 settle」的觀察訊號，填值與送出皆走真實 UI 操作。
        """
        self._min_price = min_price
        self._max_price = max_price
        waited, timed_out = self._wait_param_object_stable()
        self.log.debug("settle 等待 %.1fs timeout=%s → 填值 min=%s max=%s", waited, timed_out, min_price, max_price)
        self._fill_price_inputs()
        return self

    def _wait_param_object_stable(
        self, stable_for: float = 5, poll: float = 0.2, timeout: float = 15.0
    ) -> tuple[float, bool]:
        """等待確認鈕將送出的 React 參數物件穩定（連續 stable_for 秒參照不再改變）。

        以「物件參照在一段時間內未被重建」作為上層停止 re-render 的訊號，比死等固定秒數可靠：
        載入快就早點放行、慢就多等。逾時則放行（盡力而為，避免無限等待）。
        回傳 (等待秒數, 是否逾時) 供觀察。
        """
        start = time.monotonic()
        deadline = start + timeout
        last_token: int | None = None
        stable = 0.0
        while time.monotonic() < deadline:
            token = self._param_object_token()
            if token is not None and token == last_token:
                stable += poll
                if stable >= stable_for:
                    return time.monotonic() - start, False
            else:
                stable = 0.0
                last_token = token
            time.sleep(poll)
        return time.monotonic() - start, True

    def _param_object_token(self) -> int | None:
        """回傳確認鈕將送出之參數物件的「身分識別碼」。

        同一個物件回傳相同碼、被重建成新物件則回傳新碼，藉此偵測它是否仍在被重建。
        以不可列舉屬性標記，不影響送出邏輯。
        """
        return self.driver.execute_script(
            "const el=document.querySelector('#priceS'); if(!el) return null;"
            "const fk=Object.keys(el).find(k=>k.startsWith('__reactFiber$')); if(!fk) return null;"
            "let f=el[fk];"
            "while(f){ const p=f.memoizedProps;"
            "  if(p && p.menuSearchParameter && p.onMenuSearch){"
            "    const t=p.menuSearchParameter;"
            "    if(!t.__stableToken){"
            "      window.__stableSeq=(window.__stableSeq||0)+1;"
            "      Object.defineProperty(t,'__stableToken',{value:window.__stableSeq,enumerable:false});"
            "    }"
            "    return t.__stableToken;"
            "  }"
            "  f=f.return; }"
            "return null;"
        )

    def _fill_price_inputs(self) -> None:
        if self._min_price is not None:
            self.type_text(self.MIN_PRICE_INPUT, str(self._min_price))
        if self._max_price is not None:
            self.type_text(self.MAX_PRICE_INPUT, str(self._max_price))

    def apply_price_filter(self, timeout: float = 10.0) -> Self:
        """按「確認」套用價格篩選，並等待 URL 帶出所設定的價格參數。

        重複套用相同區間時 URL 可能與套用前相同，故不以「URL 是否改變」判斷成敗
        （否則沒變化會被誤判成失敗而拋錯）；改為驗證 URL 是否出現對應的價格參數
        （min → `_advPriceS`、max → `_advPriceE`）。
        """
        expected = self._expected_price_params()
        self.click(self.CONFIRM_BUTTON)
        if not self._wait_url_contains(expected, timeout):
            raise TimeoutException(
                f"價格篩選：點確認後 URL 未出現預期參數 {expected}，實際={self.driver.current_url}"
            )
        self.find(self.PRODUCT_CARDS)
        return self

    def _expected_price_params(self) -> list[str]:
        """依目前設定的價格區間，組出 URL 應出現的 query 片段。"""
        parts: list[str] = []
        if self._min_price is not None:
            parts.append(f"_advPriceS={self._min_price}")
        if self._max_price is not None:
            parts.append(f"_advPriceE={self._max_price}")
        return parts

    # --- 內部 ---
    def _refresh_results(
        self,
        action: Callable[[], None],
        idle_timeout: float = 6.0,
        retries: int = 5,
        retry_interval: float = 1.0,
    ) -> None:
        """執行排序後，等待結果重整完成再讓呼叫端讀取。

        排序會改變 URL（sort 改 `searchType`），故以「URL 變化」作為重整已提交的可靠訊號
        （導航中會延長等待）。點擊偶發未生效（URL 未變）時，最多重試 retries 次、每次間隔
        retry_interval 秒；若點擊其實已生效只是慢，_wait_url_changed 會先行返回而不會重試。
        """
        self._wait_page_ready()
        for attempt in range(1, retries + 1):
            old_url = self.driver.current_url
            action()
            if self._wait_url_changed(old_url, idle_timeout):
                self.find(self.PRODUCT_CARDS)
                return
            self.log.debug("排序未生效（第 %d/%d 次嘗試），%.0fs 後重試", attempt, retries, retry_interval)
            if attempt < retries:
                time.sleep(retry_interval)
        raise TimeoutException(f"排序後結果頁未如預期更新（已重試 {retries} 次）")

    def _wait_url_changed(self, old_url: str, idle_timeout: float) -> bool:
        """輪詢等待 URL 變化；頁面導航中則持續等待，僅在閒置逾時才回傳 False。"""
        deadline = time.monotonic() + idle_timeout
        while time.monotonic() < deadline:
            if self.driver.current_url != old_url:
                return True
            if self.driver.execute_script("return document.readyState") != "complete":
                deadline = time.monotonic() + idle_timeout  # 導航中，延長等待
            time.sleep(0.3)
        return False

    def _wait_url_contains(self, fragments: list[str], idle_timeout: float) -> bool:
        """輪詢等待 URL 含有全部指定片段；導航中持續等待，僅在閒置逾時才回傳 False。"""
        deadline = time.monotonic() + idle_timeout
        while time.monotonic() < deadline:
            url = self.driver.current_url
            if all(f in url for f in fragments):
                return True
            if self.driver.execute_script("return document.readyState") != "complete":
                deadline = time.monotonic() + idle_timeout  # 導航中，延長等待
            time.sleep(0.3)
        return False

    def _wait_page_ready(self) -> None:
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
