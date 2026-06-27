"""統一的 logger 取得入口；輸出等級由環境變數控制。

用法：
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.debug("關鍵判斷訊息…")

平常（預設 INFO）不會印出 debug 訊息；需要除錯時以 `DEBUG=true`（或
`LOG_LEVEL=DEBUG`）執行即可看到。搭配 pytest 時加 `-s` 讓訊息即時顯示。
"""
import logging
import sys

from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """回傳設定好的 logger；等級依 settings.LOG_LEVEL（受 DEBUG / LOG_LEVEL 環境變數控制）。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    return logger
