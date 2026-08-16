from __future__ import annotations

import sys

from loguru import logger

from config import LOG_FILE

_CONFIGURED = False


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.touch(exist_ok=True)

    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(
        LOG_FILE,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    _CONFIGURED = True
