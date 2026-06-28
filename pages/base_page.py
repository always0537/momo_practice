"""所有 Page Object 的基底。

Playwright 的 Locator 內建自動等待（auto-waiting），互動前會自動等元素可操作，
因此這裡不需像 Selenium 版那樣封裝大量顯式等待；BasePage 僅保留共用的 page 參照、
logger 與導覽入口，各頁面直接以 `self.page.locator(...)` 操作即可。

定位子（locator）一律以字串選擇器表示：CSS 直接寫；XPath 以 `xpath=` 前綴。
"""
from __future__ import annotations

from playwright.sync_api import Page

from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.log = get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
