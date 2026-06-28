"""Playwright 瀏覽器工廠：依設定啟動瀏覽器並建立 context，集中管理啟動邏輯。

把「啟動瀏覽器 / 建立 context」的細節集中在此，讓 conftest 的 fixtures 保持精簡。
瀏覽器需先以 `playwright install` 安裝。
"""
from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Playwright

from config.settings import settings


def launch_browser(pw: Playwright) -> Browser:
    """依 settings 啟動並回傳瀏覽器。"""
    browser_type = getattr(pw, settings.BROWSER, None)
    if browser_type is None:
        raise ValueError(f"尚未支援的瀏覽器：{settings.BROWSER}（可選 chromium / firefox / webkit）")

    launch_kwargs: dict = {"headless": settings.HEADLESS}
    if settings.BROWSER_CHANNEL:
        launch_kwargs["channel"] = settings.BROWSER_CHANNEL
    if settings.BROWSER == "chromium":
        # 降低被偵測為自動化的機率
        launch_kwargs["args"] = ["--disable-blink-features=AutomationControlled"]

    return browser_type.launch(**launch_kwargs)


def new_context(browser: Browser) -> BrowserContext:
    """建立並回傳一個全新的 context（每條測試獨立，天然隔離 cookie / storage）。"""
    return browser.new_context(
        viewport={"width": settings.WINDOW_WIDTH, "height": settings.WINDOW_HEIGHT},
        locale="zh-TW",
    )
