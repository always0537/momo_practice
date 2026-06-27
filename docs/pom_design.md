# POM 設計 — momo 搜尋測試

依 [test_cases.md](test_cases.md) 的 17 條 TC 反推所需的 Page Object 與成員。
原則：**只規劃 TC 會用到的 property / method**，未被任何 TC 涵蓋的元件不納入
（例：月銷量 / 新上市排序、mo 點加碼等 checkbox、分頁、登入 / 購物車）。

## Page Object 一覽

| PO | 角色 | 備註 |
|----|------|------|
| `BasePage` | 共用等待 / 互動封裝 | 已存在，所有頁面繼承 |
| `HomePage` | 首頁搜尋區進入點 | 輸入框、按鈕、自動完成 |
| `SearchResultsPage` | 搜尋結果頁 | 排序列、價格篩選、結果列表 |
| `ProductCard` | 單張商品卡片（component） | 由結果頁產生，封裝單卡資料與廣告判斷 |

---

## HomePage

對應 TC：IN-01〜IN-03、BT-01〜BT-02、AC-01〜AC-04

| 成員 | 類型 | 用途 | 服務的 TC |
|------|------|------|-----------|
| `SEARCH_INPUT` | locator | 搜尋輸入框 | IN-01〜03, AC-01〜04, BT-02 |
| `SEARCH_BUTTON` | locator | 搜尋按鈕 | BT-01, BT-02 |
| `SUGGESTION_ITEMS` | locator | 自動完成建議項清單 | AC-01〜04 |
| `open_home()` | method | 開啟首頁 | 全部 |
| `type_keyword(text)` | method | 於輸入框輸入文字 | IN-01〜03, AC-* , BT-02 |
| `get_input_value()` | method | 讀取輸入框現值 | IN-01, IN-02 |
| `clear_input()` | method | 清空輸入框 | AC-04 |
| `submit_by_enter()` | method | 按 Enter 送出 → 回傳 `SearchResultsPage` | IN-03 |
| `click_search()` | method | 點搜尋鈕 → 回傳 `SearchResultsPage` | BT-02 |
| `is_search_button_ready()` | method | 按鈕是否可見且 enabled | BT-01 |
| `suggestions()` | method | 取得建議項文字清單 | AC-01, AC-02 |
| `is_suggestion_visible()` | method | 建議清單是否顯示 | AC-01, AC-04 |
| `click_suggestion(index)` | method | 點擊第 N 筆建議 → 回傳 `SearchResultsPage` | AC-03 |

---

## SearchResultsPage

對應 TC：IN-04、BT-02、SO-01〜SO-04、PF-01〜PF-03

| 成員 | 類型 | 用途 | 服務的 TC |
|------|------|------|-----------|
| `SEARCH_INPUT` | locator | 結果頁頂部搜尋框（驗關鍵字保留） | IN-04 |
| `SORT_PRICE` | locator | 「價格」排序鈕 | SO-01, SO-02 |
| `SORT_RATING` | locator | 「評價」排序鈕 | SO-03, SO-04 |
| `MIN_PRICE_INPUT` | locator | 最低價輸入框 | PF-01, PF-02 |
| `MAX_PRICE_INPUT` | locator | 最高價輸入框 | PF-01, PF-03 |
| `CONFIRM_BUTTON` | locator | 價格篩選「確認」鈕 | PF-01〜03 |
| `PRODUCT_CARDS` | locator | 商品卡片集合 | BT-02, SO-*, PF-* |
| `get_keyword_in_box()` | method | 讀取頂部搜尋框現值 | IN-04 |
| `product_titles()` | method | 所有結果標題（相關性比對） | BT-02 |
| `products(exclude_ads=True)` | method | 回傳 `ProductCard` 清單，預設過濾廣告 | SO-*, PF-* |
| `sort_by_price()` | method | 點價格排序（可重複呼叫切換方向） | SO-01, SO-02 |
| `sort_by_rating()` | method | 點評價排序 | SO-03, SO-04 |
| `set_price_range(min, max)` | method | 填最低 / 最高價（None 則略過該欄） | PF-01〜03 |
| `apply_price_filter()` | method | 按「確認」套用篩選 | PF-01〜03 |

---

## ProductCard（component）

封裝單張卡片，供排序 / 篩選斷言取值；由 `SearchResultsPage.products()` 產生。
對應 TC：SO-01〜SO-04、PF-01〜PF-03

| 成員 | 類型 | 用途 | 服務的 TC |
|------|------|------|-----------|
| `PRICE` | locator | 卡片價格 | SO-01, SO-02, PF-* |
| `STARS` | locator | 星等 | SO-03, SO-04 |
| `AD_BADGE` | locator | 廣告標記（判斷是否為廣告卡） | SO-*, PF-*（過濾用） |
| `price()` | method | 價格數值（去 `$` 與逗號轉 int） | SO-01, SO-02, PF-* |
| `rating()` | method | 星等數值（float） | SO-03, SO-04 |
| `is_ad()` | method | 是否為廣告卡片 | SO-*, PF-*（過濾用） |

---

## TC → PO Scope 對照

| TC | HomePage | SearchResultsPage | ProductCard |
|----|----------|-------------------|-------------|
| IN-01 | ✅ | | |
| IN-02 | ✅ | | |
| IN-03 | ✅ | ✅（導頁後） | |
| IN-04 | ✅（送出） | ✅ | |
| BT-01 | ✅ | | |
| BT-02 | ✅ | ✅ | |
| AC-01 | ✅ | | |
| AC-02 | ✅ | | |
| AC-03 | ✅ | ✅（導頁後） | |
| AC-04 | ✅ | | |
| SO-01 | | ✅ | ✅ |
| SO-02 | | ✅ | ✅ |
| SO-03 | | ✅ | ✅ |
| SO-04 | | ✅ | ✅ |
| PF-01 | | ✅ | ✅ |
| PF-02 | | ✅ | ✅ |
| PF-03 | | ✅ | ✅ |
