"""集中管理測試的環境設定，可由環境變數覆寫，方便 CI 與本機切換。"""
import os


class Settings:
    # 受測站台
    BASE_URL: str = os.getenv("MOMO_BASE_URL", "https://www.momoshop.com.tw/")

    # 瀏覽器設定
    BROWSER: str = os.getenv("BROWSER", "chrome")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

    # 記錄設定：DEBUG=true 會印出除錯訊息（等同 LOG_LEVEL=DEBUG）；
    # 也可用 LOG_LEVEL 直接指定（DEBUG / INFO / WARNING…）。
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()

    # 等待逾時（秒）
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "15"))

    # 視窗大小
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))


settings = Settings()
