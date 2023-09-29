from pathlib import Path
from typing import Any, cast

_APP_KEY = "core"


class ApplicationConfigManager:
    def __init__(self, config: dict[Any, Any]) -> None:
        # for some reason, the passed argument 'config' isn't of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible
        # just exposing the values that are actual of value for cross cutting
        # concerns
        self.working_dir = Path(config[_APP_KEY]["working_dir"]).resolve()


def config() -> ApplicationConfigManager:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    return cast(
        ApplicationConfigManager, Application().cross_cutting_concerns.config_manager()
    )
