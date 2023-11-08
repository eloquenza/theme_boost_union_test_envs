import secrets
import socket
import string
from contextlib import closing
from pathlib import Path
from string import Template
from typing import Any, cast

import jinja2

from . import config


class TemplateEngine:
    def __init__(self) -> None:
        # used to manage access to all template files, so we can easily copy them into our test environments.
        # copying is managed by the testbed itself currently
        files_in_cwd = (Path(__file__).parent / "templates").glob("**/*")
        self.template_files = [file for file in files_in_cwd if file.is_file()]

    def test_environment_overview_html(self, infrastructures: dict[str, Any]) -> None:
        index_html = Path(__file__).parent / "templates" / "index.html.j2"
        with index_html.open("r") as f:
            template = jinja2.Template(f.read())
        rendered_text = template.render(infrastructures)
        index_html = config().nginx_dir / "index.html"
        index_html.write_text(rendered_text)

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
        self, template_path: Path, infrastructure_name: str, version: str
    ) -> None:
        env_file = template_path / ".env"
        compose_safe_version = self._create_compose_safe_version_string(version)
        substitutes = {
            "REPLACE_COMPOSE_NAME": f"{infrastructure_name+'-moodle-'+compose_safe_version}",
            "REPLACE_MOODLE_SOURCE_PATH": f"{template_path / 'moodle'}",
            "REPLACE_PASSWORD": self._create_new_admin_pw(),
            "REPLACE_MOODLE_WEB_PORT": self._find_free_port(),
            "REPLACE_MOODLE_DB_PORT": self._find_free_port(),
        }
        template = Template(env_file.read_text())
        replaced_strings = template.substitute(substitutes)
        env_file.write_text(replaced_strings)

    def _create_compose_safe_version_string(self, version: str) -> str:
        return version.replace(".", "_")

    def _create_new_admin_pw(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(32))

    def _find_free_port(self) -> Any:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]


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
