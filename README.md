# momo 搜尋功能自動化測試

針對 [momo 購物網](https://www.momoshop.com.tw/) 首頁的搜尋功能進行自動化 UI 測試，採用 **Playwright + pytest**，並以 **Page Object Model (POM)** 組織程式碼。

## 環境需求

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Playwright 瀏覽器（以 `playwright install` 安裝，預設使用內建 Chromium，跨機最穩定）

## 安裝

```bash
# 安裝 Python 套件
uv sync

# 安裝 Playwright 瀏覽器（預設只需 chromium）
uv run playwright install chromium
```

> 若想改用其他引擎（firefox / webkit），請一併 `uv run playwright install firefox webkit`。

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

> 測試失敗時會自動截圖到 `reports/<測試名稱>.png`。

## 可用環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `MOMO_BASE_URL` | `https://www.momoshop.com.tw/` | 受測站台 |
| `BROWSER` | `chromium` | Playwright 引擎（chromium / firefox / webkit） |
| `CHANNEL` | （空） | 改用系統瀏覽器通道（如 `chrome`、`msedge`）；留空用內建瀏覽器 |
| `HEADLESS` | `true` | 是否無頭模式 |
| `DEBUG` | `false` | `true` 等同 `LOG_LEVEL=DEBUG` |
| `LOG_LEVEL` | `INFO` | 記錄等級（DEBUG / INFO / WARNING…） |
| `EXPLICIT_WAIT` | `15` | 元素操作預設逾時（秒，內部換算為毫秒） |
| `PAGE_LOAD_TIMEOUT` | `30` | 頁面導航逾時（秒，內部換算為毫秒） |
| `WINDOW_WIDTH` | `1920` | viewport 寬度 |
| `WINDOW_HEIGHT` | `1080` | viewport 高度 |

## 專案結構

```
momo_practice/
├── config/
│   └── settings.py              # 集中設定（可由環境變數覆寫）
├── pages/                       # Page Object Model
│   ├── base_page.py             # 共用 page 參照 / 導覽入口
│   ├── home_page.py             # 首頁搜尋區（輸入框、按鈕、自動完成）
│   ├── search_results_page.py   # 搜尋結果頁（排序、價格篩選）
│   └── product_card.py          # 單張商品卡片 component
├── utils/
│   ├── browser_factory.py       # Playwright 瀏覽器 / context 工廠
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
├── conftest.py                  # pytest fixtures（browser / page / home_page）
├── reports/                     # 測試輸出（失敗截圖；git 忽略）
└── pyproject.toml
```

## 文件

- [測試案例清單](docs/test_cases.md)
- [POM 設計說明](docs/pom_design.md)
