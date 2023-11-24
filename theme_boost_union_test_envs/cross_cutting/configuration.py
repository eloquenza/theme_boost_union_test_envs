import sys
from pathlib import Path
from typing import Any, cast

import yaml
from packaging import version

from ..exceptions import BoostUnionTestEnvValueError

_CORE_KEY = "core"
_REPO_KEY = "repos"
_NGINX_KEY = "nginx"


class ApplicationConfigManager:
    def __init__(
        self,
        config: dict[Any, Any],
        environment_file: Path,
        moodle_versions_to_php_versions: dict[Any, Any],
    ) -> None:
        # for some reason, the passed argument 'config' isn't of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible

        # reading environment-related configs from yaml
        with environment_file.open("r") as env:
            # don't forget, it's python: no need to forward_declare before
            environment = yaml.safe_load(env)

        # converting the int/str values from the read yaml into actual version types
        self.moodle_versions_to_php_versions = {
            version.parse(str(moodle_ver)): [
                version.parse(str(ver)) for ver in php_vers
            ]
            for moodle_ver, php_vers in moodle_versions_to_php_versions.items()
        }

        # just exposing the values that are actual of value for cross cutting
        # concerns
        # core related settings
        self.working_dir = Path(environment["working_dir"]).resolve()
        # implicitly truthy as python transforms yes and no
        self.is_proxied = environment["proxied"]
        self.infra_yaml = self.working_dir / "infrastructure.yaml"
        # nginx related settings
        self.nginx_dir: Path = self.working_dir / config[_CORE_KEY][_NGINX_KEY]["dir"]
        self.base_url = environment[_NGINX_KEY]["base_url"]
        # if we are setting up new test environments behind a proxy, these NEED # to be set so the reverse proxy will actually work correct
        if self.is_proxied and (
            not environment[_NGINX_KEY]["cert_chain_path"]
            or not environment[_NGINX_KEY]["cert_key_path"]
            or not environment[_NGINX_KEY]["overview_page_path"]
        ):
            raise BoostUnionTestEnvValueError(
                "Certificate file paths as well as path for the overview webpage must be set"
            )
        # do not try to provide a default here, no sensible option left
        self.cert_chain_path = environment[_NGINX_KEY]["cert_chain_path"]
        self.cert_key_path = environment[_NGINX_KEY]["cert_key_path"]
        # default to working_dir/index.html; allows for debugging it
        self.overview_page_path = (
            self.working_dir / "index.html"
            if not environment[_NGINX_KEY]["overview_page_path"]
            else Path(environment[_NGINX_KEY]["overview_page_path"])
        )
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
