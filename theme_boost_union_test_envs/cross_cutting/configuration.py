import sys
from pathlib import Path
from typing import Any, cast

import yaml

_CORE_KEY = "core"
_REPO_KEY = "repos"
_NGINX_KEY = "nginx"


class ApplicationConfigManager:
    def __init__(self, config: dict[Any, Any], environment_file: Path) -> None:
        # for some reason, the passed argument 'config' isn't of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible
        # just exposing the values that are actual of value for cross cutting
        # concerns

        # reading environment-related configs from yaml
        with environment_file.open("r") as env:
            # don't forget, it's python: no need to forward_declare before
            environment = yaml.safe_load(env)

        # core related settings
        self.working_dir = Path(environment["working_dir"]).resolve()
        self.is_proxied = True if environment["proxied"] == "yes" else False
        self.infra_yaml = self.working_dir / "infrastructure.yaml"
        # nginx related settings
        self.nginx_dir: Path = self.working_dir / config[_CORE_KEY][_NGINX_KEY]["dir"]
        self.base_url = environment[_NGINX_KEY]["base_url"]
        self.cert_chain_path = environment[_NGINX_KEY]["cert_chain_path"]
        self.cert_key_path = environment[_NGINX_KEY]["cert_key_path"]
        self.overview_page_path = Path(environment[_NGINX_KEY]["overview_page_path"])
        # moodle related settings
        self.moodle_docker_dir = (
            self.working_dir / config[_REPO_KEY]["moodle_docker"]["dir"]
        )


def config() -> ApplicationConfigManager:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    return cast(
        ApplicationConfigManager, Application().cross_cutting_concerns.config_manager()
    )
