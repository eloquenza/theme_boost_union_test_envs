from typing import Any

from dependency_injector import containers, providers

APP_KEY = "core"


class ApplicationConfigManager:
    def __init__(self, config: dict[Any, Any]) -> None:
        # for some reason, the passed argument 'config' isn't of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible
        self.working_dir = config[APP_KEY]["working_dir"]
        self.moodle_cache_dir = config[APP_KEY]["moodle_cache_dir"]
