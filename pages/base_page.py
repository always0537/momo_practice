"""所有 Page Object 的基底，封裝共用的等待 / 互動方法。

把 WebDriverWait、尋找元素、點擊、輸入等行為集中在這裡，
讓各頁面只需專注在「定位子 + 業務動作」，提高可維護性與穩定性。
"""
from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from utils.logger import get_logger

Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver: WebDriver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, settings.EXPLICIT_WAIT)
        self.log = get_logger(self.__class__.__name__)

    # --- 導覽 ---
    def open(self, url: str) -> None:
        self.driver.get(url)

    # --- 等待 + 尋找 ---
    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: Locator, timeout: float | None = None) -> WebElement:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        self.wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    # --- 互動 ---
    def click(self, locator: Locator, timeout: float | None = None) -> None:
        self.find_clickable(locator, timeout).click()

    def type_text(self, locator: Locator, text: str) -> None:
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def is_visible(self, locator: Locator) -> bool:
        try:
            return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except TimeoutException:
            return False

    def wait_invisible(self, locator: Locator, timeout: float | None = None) -> bool:
        """等待元素消失（不可見或從 DOM 移除）；逾時則回傳 False。"""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
