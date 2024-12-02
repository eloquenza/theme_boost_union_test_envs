import pprint
import sys
from pathlib import Path
from typing import Any, Tuple, cast

import yaml
from packaging import version

from ..exceptions import BoostUnionTestEnvValueError

# Core related keys in config
PWD = "working_dir"

# Repo related keys in config
REPO = "repos"
MDL_DKR = "moodle_docker"
URL = "url"

# Proxy related keys in env file
NGINX = "nginx"
WWW_BASE = "base_url"
CERT_PATH = "cert_chain_path"
PKEY_PATH = "cert_key_path"
HTML_PATH = "overview_page_path"
PROXY = "proxied"
SOFTLINKED_DIR = "softlinked_nginx_config_path"


class ApplicationConfigManager:
    def __init__(
        self,
        config: dict[Any, Any],
        moodle_versions_to_php_versions: dict[Any, Any],
        supported_plugins: dict[Any, Any],
        environment_file: Path,
    ) -> None:
        # for some reason, the passed arguments 'config' and 'moodle_versions_to_php_versions' are not of type providers.Configuration anymore, which makes saving it and accessing all elements with the dot notation not possible

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

        self.supported_plugins = supported_plugins

        # just exposing the values that are actual of value for cross cutting
        # concerns
        # path related settings
        self.working_dir = self.get_path(environment[PWD])
        self.infra_yaml = self.working_dir / "infrastructure.yaml"
        # nginx related settings
        self.nginx_dir = self.working_dir / ".nginx/"
        self.softlinked_nginx_path = Path(environment[NGINX][SOFTLINKED_DIR])
        self.base_url = environment[NGINX][WWW_BASE]
        # implicitly truthy as python transforms yes and no
        self.is_proxied = environment[PROXY]
        # if we are setting up new test environments behind a proxy, these NEED # to be set so the reverse proxy will actually work correct
        if self.is_proxied and (
            not environment[NGINX][CERT_PATH]
            or not environment[NGINX][PKEY_PATH]
            or not environment[NGINX][HTML_PATH]
        ):
            raise BoostUnionTestEnvValueError(
                "Certificate file paths as well as path for the overview webpage must be set"
            )
        # do not try to provide a default here, no sensible option left
        self.cert_chain_path = environment[NGINX][CERT_PATH]
        self.cert_key_path = environment[NGINX][PKEY_PATH]
        # default to working_dir/index.html; allows for debugging it
        self.overview_page_path = (
            self.working_dir
            if not environment[NGINX][HTML_PATH]
            else Path(environment[NGINX][HTML_PATH])
        )
        self.overview_page_index = self.overview_page_path / "index.html"
        # moodle related settings
        self.moodle_cache_dir = self.working_dir / ".moodles/"
        self.moodle_docker_dir = self.working_dir / ".moodle-docker"
        self.moodle_docker_repo_url = config[REPO][MDL_DKR][URL]

    def get_path(self, path_name: str) -> Path:
        return Path(path_name).resolve()

    def get_plugin_information(self, plugin_name: str) -> Tuple[str, str]:
        repo_url, install_folder = config().supported_plugins[plugin_name].values()
        return repo_url, install_folder


def config() -> ApplicationConfigManager:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    return cast(
        ApplicationConfigManager, Application().cross_cutting_concerns.config_manager()
    )
