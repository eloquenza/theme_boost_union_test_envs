import secrets
import socket
import string
from contextlib import closing
from pathlib import Path
from string import Template
from typing import Any, cast

import jinja2
from packaging import version

from ..exceptions import UnsupportedMoodleVersionError
from . import config, log, yaml_parser


class TemplateEngine:
    def __init__(self) -> None:
        self.template_path = Path(__file__).parent / "templates"
        # used to manage access to all template files, so we can easily copy them into our test environments.
        # copying is managed by the testbed itself currently
        files_in_cwd = self.template_path.glob("**/*")
        self.template_files = [file for file in files_in_cwd if file.is_file()]

    def test_environment_overview_html(self, infrastructures: dict[str, Any]) -> None:
        index_html = self.template_path / "index.html.j2"
        with index_html.open("r") as f:
            template = jinja2.Template(f.read())
        rendered_text = template.render(infrastructures)
        if config().overview_page_path.parent.exists():
            config().overview_page_path.write_text(rendered_text)

    def docker_customisation(
        self, template_path: Path, boost_union_source_dir: Path
    ) -> None:
        docker_customisation_file = template_path / "local.yml"
        substitutes = {
            "REPLACE_BOOST_UNION_SOURCE_PATH": boost_union_source_dir,
        }
        template = Template(docker_customisation_file.read_text())
        replaced_strings = template.substitute(substitutes)
        docker_customisation_file.write_text(replaced_strings)

    def environment_file(
        self, template_path: Path, infrastructure_name: str, moodle_version: str
    ) -> None:
        env_file = template_path / ".env"
        compose_safe_name = self._create_compose_safe_name(
            infrastructure_name, moodle_version
        )
        web_host = self._create_web_url(infrastructure_name, moodle_version)
        substitutes = {
            "REPLACE_COMPOSE_NAME": compose_safe_name,
            "REPLACE_MOODLE_SOURCE_PATH": f"{template_path / 'moodle'}",
            "REPLACE_PASSWORD": self._create_new_admin_pw(),
            "REPLACE_MOODLE_WEB_HOST": web_host,
            "REPLACE_MOODLE_WEB_PORT": self._find_free_port(),
            "REPLACE_MOODLE_DB_PORT": self._find_free_port(),
            "REPLACE_MOODLE_DOCKER_PHP_VERSION": self._select_fitting_docker_image_tag(
                moodle_version
            ),
        }
        template = Template(env_file.read_text())
        replaced_strings = template.substitute(substitutes)
        env_file.write_text(replaced_strings)

    def nginx_config(
        self, infrastructure_name: str, moodle_version: str, port: str
    ) -> None:
        nginx_conf_template = self.template_path / "moodle_nginx.conf"
        safe_name = self._create_compose_safe_name(infrastructure_name, moodle_version)
        new_config = config().nginx_dir / f"{safe_name}.conf"
        # TODO:
        softlinked_nginx_dir = ""
        # get only "path" from the fqdn, we don't need the domain name, called
        # location in nginx
        location = self._create_web_url(infrastructure_name, moodle_version).partition(
            config().base_url
        )[2]
        substitutes = {
            "REPLACE_LOCATION": location,
            "REPLACE_BASE_URL": config().base_url,
            "REPLACE_PORT": port,
            "REPLACE_CERT_PATH": config().cert_chain_path,
            "REPLACE_PRIVKEY_PATH": config().cert_key_path,
            "REPLACE_ACCESS_LOG_PATH": f"{softlinked_nginx_dir}/{safe_name}_proxy_access_ssl_log",
            "REPLACE_ERROR_LOG_PATH": f"{softlinked_nginx_dir}/{safe_name}_proxy_error_ssl_log",
        }
        template = Template(nginx_conf_template.read_text())
        # using safe_substitute here instead as the nginx config contains variables starting with "$", which would make the default substitute call throw an KeyError as we are not replacing the template placeholder which we do not want
        replaced_strings = template.safe_substitute(substitutes)
        new_config.write_text(replaced_strings)
        return

    def _create_web_url(
        self,
        infrastructure_name: str,
        moodle_version: str,
    ) -> str:
        web_url = f"{config().base_url}"
        if config().is_proxied:
            web_url = web_url + f"/{infrastructure_name}/{moodle_version}"
        return web_url

    def _create_compose_safe_name(
        self, infrastructure_name: str, moodle_version: str
    ) -> str:
        compose_safe_version = self._create_compose_safe_version_string(moodle_version)
        return f"{infrastructure_name+'-moodle-'+compose_safe_version}"

    def _create_compose_safe_version_string(self, version: str) -> str:
        return version.replace(".", "_")

    def _create_new_admin_pw(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(32))

    def _find_free_port(self) -> Any:
        infrastructures = yaml_parser().load_testbed_info()
        used_ports = []
        for _, data in infrastructures.items():
            for _, access_info in data["moodles"].items():
                used_ports.append(access_info["www_port"])
                used_ports.append(access_info["db_port"])
        while True:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(("", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                new_port = s.getsockname()[1]
                if new_port not in used_ports:
                    return new_port

    def _select_fitting_docker_image_tag(self, moodle_version: str) -> str:
        supported_versions = config().moodle_versions_to_php_versions
        # if given moodle version is outside of defined moodle-to-php dictionary, default to container image tag "dev", if and only if the major or minor version is higher.
        # using max(dict) here instead of just selecting the first element of the map. ensures we will not have an error just because somebody *wink* in the future updating our map does not respect the carefully chosen insertion order
        # empty string as little, dirty sentinel value
        image_tag = ""
        if (version.parse(moodle_version).major > max(supported_versions).major) or (
            version.parse(moodle_version).major == max(supported_versions).major
            and version.parse(moodle_version).minor > max(supported_versions).minor
        ):
            image_tag = "dev"
        else:
            for ver in supported_versions:
                # For the given moodle_version, we want to ideally select the newest supported php version - to ensure that we have probably no issues.
                # To do so, we iterate through our map and check if given moodle_version can be fitted to a available version.
                # As the map contains only breakpoints, i.e. Moodle versions where the supported PHP versions change, we need to iterate through the map and check if the given moodle_ver is higher than the currently selected key we are iterating over.
                # If true; take the 2nd element of it's persisted value (a tuple), which denotes the newest suppported php version
                # else: go to next iteration, selecting the next persisted moodle version string and try again
                # Using version.parse here to compare the versions, because lexigraphically comparing versions does not really work well, i.e. 3.9 would be "higher" (>) than 3.11. because it would compare the 9 to the first digit of eleven, i.e. 1.
                # Handrolling a parsing for this isn't trivial, and there isn't a official Moodle specification for how they structure Moodle versions, apparently. We could just explode the version string into tuples and compare then, or we try more reliable solutions. It mostly follows semver (X.Y.Z), but it isn't clarified it does so. It also allows release candidates (e.g. 4.3.0-rc1) or beta (e.g. 4.3.0-beta) versions. Relying on python's version.parse works from a few pre-tests. "4.3.0-beta" isn't allowed per python specification, but for backwards compatibility to older specifications, it still is transformed into "4.3.0b0"; for which the comparison work again.
                if version.parse(moodle_version) > ver:
                    image_tag = str(supported_versions[ver][1])
                    log().info(f"selecting php version {image_tag} for this container")
                    break
            # at this point, the given moodle_version is so old, we really do not support it anymore. raise exception and scold user for molesting ancient moodle versions.
        if not image_tag:
            raise UnsupportedMoodleVersionError(moodle_version)
        return image_tag


def template_engine() -> TemplateEngine:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    engine = cast(
        TemplateEngine, Application().cross_cutting_concerns.template_engine()
    )
    return engine
