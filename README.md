# momo 搜尋功能自動化測試

針對 [momo 購物網](https://www.momoshop.com.tw/) 首頁的搜尋功能進行自動化 UI 測試，採用 **Selenium + pytest**，並以 **Page Object Model (POM)** 組織程式碼。

## 環境需求

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Google Chrome（Selenium 4.6+ 內建 Selenium Manager，會自動下載對應的 chromedriver）

> 目前僅支援 Chrome；`BROWSER` 設為其他值會丟出 `ValueError`。

## 安裝

```bash
uv sync
```

## 執行測試

```bash
# 執行全部測試
uv run pytest

# 只跑 smoke（核心流程）
uv run pytest -m smoke

# 只跑搜尋相關測試
uv run pytest -m search

# 以有頭（headed）模式觀察瀏覽器
HEADLESS=false uv run pytest

# 開啟除錯訊息（需搭配 -s 即時顯示）
DEBUG=true uv run pytest -s
```

## 可用環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `MOMO_BASE_URL` | `https://www.momoshop.com.tw/` | 受測站台 |
| `BROWSER` | `chrome` | 瀏覽器（目前僅支援 chrome） |
| `HEADLESS` | `true` | 是否無頭模式 |
| `DEBUG` | `false` | `true` 等同 `LOG_LEVEL=DEBUG` |
| `LOG_LEVEL` | `INFO` | 記錄等級（DEBUG / INFO / WARNING…） |
| `EXPLICIT_WAIT` | `15` | 顯式等待逾時（秒） |
| `PAGE_LOAD_TIMEOUT` | `30` | 頁面載入逾時（秒） |
| `WINDOW_WIDTH` | `1920` | 視窗寬度 |
| `WINDOW_HEIGHT` | `1080` | 視窗高度 |

## 專案結構

```
momo_practice/
├── config/
│   └── settings.py              # 集中設定（可由環境變數覆寫）
├── pages/                       # Page Object Model
│   ├── base_page.py             # 共用等待 / 互動封裝
│   ├── home_page.py             # 首頁搜尋區（輸入框、按鈕、自動完成）
│   ├── search_results_page.py   # 搜尋結果頁（排序、價格篩選）
│   └── product_card.py          # 單張商品卡片 component
├── utils/
│   ├── driver_factory.py        # WebDriver 工廠
│   └── logger.py                # 統一 logger
├── tests/
│   ├── test_search_input.py     # 輸入框（IN-01〜04）
│   ├── test_search_button.py    # 搜尋按鈕（BT-01〜02）
│   ├── test_autocomplete.py     # 自動完成（AC-01〜04）
│   ├── test_sort.py             # 排序（SO-01〜04）
│   ├── test_price_filter.py     # 價格篩選（PF-01〜03）
│   └── test_search_edge_cases.py # 邊界 / 負向（NR-01、EG-01）
├── docs/
│   ├── test_cases.md            # 測試案例清單
│   └── pom_design.md            # POM 設計說明
├── conftest.py                  # pytest fixtures（driver / home_page）
├── reports/                     # 測試輸出（git 忽略）
└── pyproject.toml
```

## 文件

- [測試案例清單](docs/test_cases.md)
- [POM 設計說明](docs/pom_design.md)
