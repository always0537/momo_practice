"""WebDriver 工廠：依設定建立並設定瀏覽器，集中管理 driver 建立邏輯。

Selenium 4.6+ 內建 Selenium Manager，會自動下載對應的 driver，
因此這裡不需要手動指定 driver 路徑。
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config.settings import settings


def create_driver() -> webdriver.Chrome:
    """依 settings 建立並回傳已設定好的 WebDriver。"""
    browser = settings.BROWSER.lower()

    if browser == "chrome":
        return _create_chrome()

    raise ValueError(f"尚未支援的瀏覽器：{settings.BROWSER}")


def _create_chrome() -> webdriver.Chrome:
    options = ChromeOptions()

    if settings.HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
    else:
        options.add_argument("--start-maximized")  # headed 模式開啟即最大化
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 降低被偵測為自動化的機率
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    if not settings.HEADLESS:
        driver.maximize_window()  # 確保視窗最大化（--start-maximized 的雙重保險）
    return driver
