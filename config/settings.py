"""集中管理測試的環境設定，可由環境變數覆寫，方便 CI 與本機切換。"""
import os


class Settings:
    # 受測站台
    BASE_URL: str = os.getenv("MOMO_BASE_URL", "https://www.momoshop.com.tw/")

    # 瀏覽器設定
    # BROWSER：Playwright 瀏覽器引擎（chromium / firefox / webkit）。
    BROWSER: str = os.getenv("BROWSER", "chromium")
    # CHANNEL：指定使用已安裝的系統瀏覽器通道（如 chrome / msedge）；
    # 留空則使用 Playwright 內建瀏覽器（建議，跨機最穩定）。
    BROWSER_CHANNEL: str = os.getenv("CHANNEL", "")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

    # 記錄設定：DEBUG=true 會印出除錯訊息（等同 LOG_LEVEL=DEBUG）；
    # 也可用 LOG_LEVEL 直接指定（DEBUG / INFO / WARNING…）。
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()

    # 等待逾時（Playwright 以毫秒計，這裡以秒設定後換算）
    DEFAULT_TIMEOUT_MS: int = int(os.getenv("EXPLICIT_WAIT", "15")) * 1000
    NAVIGATION_TIMEOUT_MS: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30")) * 1000

    # 視窗 / viewport 大小
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))


settings = Settings()
