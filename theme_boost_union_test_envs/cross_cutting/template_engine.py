import secrets
import socket
import string
from contextlib import closing
from pathlib import Path
from string import Template
from typing import Any, cast


class TemplateEngine:
    def __init__(self) -> None:
        files_in_cwd = (Path(__file__).parent / "templates").glob("**/*")
        self.template_files = [file for file in files_in_cwd if file.is_file()]

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
        }
        template = Template(env_file.read_text())
        replaced_strings = template.substitute(substitutes)
        env_file.write_text(replaced_strings)

    def _create_compose_safe_version_string(self, version: str) -> str:
        return version.replace(".", "_")

    def _create_new_admin_pw(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(20))

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
