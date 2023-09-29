from __future__ import annotations

from typing import cast

import loguru


class ApplicationLogger:
    def __init__(self) -> None:
        self.log = loguru.logger


def log() -> loguru.Logger:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    logger = cast(ApplicationLogger, Application().cross_cutting_concerns.log())
    return logger.log
