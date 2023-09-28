from pathlib import Path
from typing import Any, cast

from dependency_injector import containers, providers

APP_KEY = "core"


class ApplicationConfigManager:
    def __init__(self, config: dict[Any, Any]) -> None:
        # for some reason, the passed argument 'config' isn't of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible
        self.working_dir = Path(config[APP_KEY]["working_dir"]).resolve()
        self.moodle_cache_dir = Path(config[APP_KEY]["moodle_cache_dir"]).resolve


def get_config() -> ApplicationConfigManager:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..di_containers import Application

    # sometimes mypy is just a funny thing.
    return cast(
        ApplicationConfigManager, Application().cross_cutting_concerns.config_manager()
    )
