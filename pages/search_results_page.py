"""搜尋結果頁 — 提供排序、價格篩選與結果取值，供測試斷言。

結果頁為 momo 舊版 UI（無 data-testid），改用 id / class / 結構選擇器。
"""
from __future__ import annotations

import time
from typing import Callable, Self

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from pages.product_card import ProductCard


class SearchResultsPage(BasePage):
    SEARCH_INPUT = "#header-search-input"  # 頂部搜尋框（驗關鍵字保留）
    SORT_PRICE = "xpath=//li[contains(@class,'priceHeight') and normalize-space()='價格']"
    SORT_RATING = "xpath=//li[contains(@class,'priceHeight') and normalize-space()='評價']"
    MIN_PRICE_INPUT = "#priceS"
    MAX_PRICE_INPUT = "#priceE"
    CONFIRM_BUTTON = "a.priceBtn"
    PRODUCT_CARDS = "li.listAreaLi"
    NO_RESULTS = ".noSearchResultWrapper"  # 查無結果空狀態容器

    _min_price: int | None = None
    _max_price: int | None = None

    # --- 抵達 ---
    def wait_until_loaded(self) -> Self:
        """等待已抵達搜尋結果頁且結果區已渲染（商品卡或查無結果空狀態其一出現）。

        Playwright 的 click 不會等待導航完成，導頁方法若點完即回傳，後續讀取（如關鍵字
        保留、排序列）可能搶在結果頁就緒之前——讀到舊頁或尚未 hydrate 的值而 flaky。
        故導頁方法回傳前統一呼叫此法，顯式等到結果頁就緒（含查無結果情境）再放行。
        """
        self.page.wait_for_url("**/search/**")
        self.page.locator(f"{self.PRODUCT_CARDS}, {self.NO_RESULTS}").first.wait_for()
        return self

    # --- 查詢 ---
    def get_keyword_in_box(self) -> str:
        """讀取結果頁頂部搜尋框現值。"""
        return self.page.locator(self.SEARCH_INPUT).input_value()

    def products(self, exclude_ads: bool = True) -> list[ProductCard]:
        """回傳結果卡片清單；預設過濾掉廣告卡（`.sponsor-tag`）。"""
        cards = self.page.locator(self.PRODUCT_CARDS)
        cards.first.wait_for()  # 等待至少一張卡片出現
        result = [ProductCard(cards.nth(i)) for i in range(cards.count())]
        return [c for c in result if not c.is_ad()] if exclude_ads else result

    def product_titles(self, exclude_ads: bool = True) -> list[str]:
        return [c.title for c in self.products(exclude_ads) if c.title]

    def product_count(self) -> int:
        """目前頁面的商品卡數量（不等待，供『查無結果』情境直接點數）。"""
        return self.page.locator(self.PRODUCT_CARDS).count()

    def is_no_results_shown(self) -> bool:
        """是否顯示『查無結果』空狀態（搜尋不到符合商品時 momo 會渲染此區塊）。"""
        try:
            self.page.locator(self.NO_RESULTS).wait_for(state="visible")
            return True
        except PlaywrightTimeoutError:
            return False

    # --- 排序 ---
    def sort_by_price(self) -> Self:
        """點價格排序（重複呼叫可切換遞增 / 遞減）。"""
        self._refresh_results(lambda: self.page.locator(self.SORT_PRICE).click())
        return self

    def sort_by_rating(self) -> Self:
        self._refresh_results(lambda: self.page.locator(self.SORT_RATING).click())
        return self

    def _sort_direction(self, sort_locator: str) -> str | None:
        """讀取排序欄目前 UI 標示的方向。

        momo 以排序 li 的 class token 標示：`down`=高→低（遞減）、`up`=低→高（遞增）、
        兩者皆無=未排序。據此讓測試「依 UI 呈現的方向」驗對應排序，而非靠點擊次數推斷。
        """
        classes = (self.page.locator(sort_locator).get_attribute("class") or "").split()
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
        return self.page.evaluate(
            """() => {
                const el = document.querySelector('#priceS');
                if (!el) return null;
                const fk = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
                if (!fk) return null;
                let f = el[fk];
                while (f) {
                    const p = f.memoizedProps;
                    if (p && p.menuSearchParameter && p.onMenuSearch) {
                        const t = p.menuSearchParameter;
                        if (!t.__stableToken) {
                            window.__stableSeq = (window.__stableSeq || 0) + 1;
                            Object.defineProperty(t, '__stableToken', {value: window.__stableSeq, enumerable: false});
                        }
                        return t.__stableToken;
                    }
                    f = f.return;
                }
                return null;
            }"""
        )

    def _fill_price_inputs(self) -> None:
        if self._min_price is not None:
            self.page.locator(self.MIN_PRICE_INPUT).fill(str(self._min_price))
        if self._max_price is not None:
            self.page.locator(self.MAX_PRICE_INPUT).fill(str(self._max_price))

    def apply_price_filter(self, timeout: float = 10000) -> Self:
        """按「確認」套用價格篩選，並等待 URL 帶出所設定的價格參數。

        重複套用相同區間時 URL 可能與套用前相同，故不以「URL 是否改變」判斷成敗
        （否則沒變化會被誤判成失敗而拋錯）；改為驗證 URL 是否出現對應的價格參數
        （min → `_advPriceS`、max → `_advPriceE`）。
        """
        expected = self._expected_price_params()
        self.page.locator(self.CONFIRM_BUTTON).click()
        try:
            self.page.wait_for_url(lambda url: all(f in url for f in expected), timeout=timeout)
        except PlaywrightTimeoutError as exc:
            raise PlaywrightTimeoutError(
                f"價格篩選：點確認後 URL 未出現預期參數 {expected}，實際={self.page.url}"
            ) from exc
        self.page.locator(self.PRODUCT_CARDS).first.wait_for()
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
        idle_timeout: float = 6000,
        retries: int = 5,
        retry_interval: float = 1.0,
    ) -> None:
        """執行排序後，等待結果重整完成再讓呼叫端讀取。

        排序會改變 URL（sort 改 `searchType`），故以「URL 變化」作為重整已提交的可靠訊號。
        wait_for_url 有固定 idle_timeout 上限（非無限等待）；逾時後**不可貿然重試**，因為排序欄
        重複點擊會切換遞增/遞減方向——若上一次點擊其實已生效只是慢，再點一次反而把方向切回。
        故逾時後先確認 URL 是否其實已變：已變則視為成功直接返回，僅在確實未變時才重試點擊
        （最多 retries 次、每次間隔 retry_interval 秒）。
        """
        self.page.wait_for_load_state("domcontentloaded")
        for attempt in range(1, retries + 1):
            old_url = self.page.url
            action()
            try:
                self.page.wait_for_url(lambda url: url != old_url, timeout=idle_timeout)
            except PlaywrightTimeoutError:
                if self.page.url == old_url:  # 點擊確實未生效，才重試
                    self.log.debug("排序未生效（第 %d/%d 次嘗試），%.0fs 後重試", attempt, retries, retry_interval)
                    if attempt < retries:
                        time.sleep(retry_interval)
                    continue
                # URL 已變，只是慢過了 idle_timeout：點擊已生效，當作成功
                self.log.debug("排序逾時但 URL 已變，視為已生效")
            self.page.locator(self.PRODUCT_CARDS).first.wait_for()
            return
        raise PlaywrightTimeoutError(f"排序後結果頁未如預期更新（已重試 {retries} 次）")
