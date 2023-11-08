import shutil
import subprocess
from pathlib import Path

from ..cross_cutting import log


class TestContainer:
    def __init__(self, container_path: Path) -> None:
        # TODO: check if path exists
        self.path = container_path
        self.compose_script = "bin/moodle-docker-compose"

    def create(self) -> None:
        self._run_docker_command("create")

    def start(self) -> None:
        self._run_docker_command("up -d && bin/moodle-docker-wait-for-db")
        self._configure_manual_testing()
        host, port, pw = self.container_access_info()
        log().info("Please access the created Moodle container here:")
        log().info(f"Enter the following URL into your browser: http://{host}:{port}/")
        log().info(f"Login as admin with pw: {pw}")

    def restart(self) -> None:
        self._run_docker_command("restart")

    def stop(self) -> None:
        self._run_docker_command("stop")

    def destroy(self) -> None:
        self._run_docker_command("down")
        # TODO: removing the directory shouldn't be the concern of the TestContainer itself
        if self.path.exists():
            shutil.rmtree(self.path)

    def container_access_info(self) -> tuple[str, str, str]:
        host = self._extract_from_env("MOODLE_DOCKER_WEB_HOST")
        port = self._extract_from_env("MOODLE_DOCKER_WEB_PORT")
        admin_password = self._extract_from_env("MOODLE_ADMIN_PASSWORD")
        return host, port, admin_password

    def _configure_manual_testing(self) -> None:
        admin_email = "admin@example.com"
        version = self.path.name
        infrastructure = self.path.parent.parent.name
        short_name = f"{infrastructure} - {version}"
        full_name = f"{infrastructure} - {version}"
        summary = f"{infrastructure} - {version}"
        # create the correct tables on the database server
        self._run_local_php_script(
            "admin/cli/install_database.php",
            f'--agree-license --fullname="{full_name}" --shortname="{short_name}" --summary="{summary}" --adminpass=$MOODLE_ADMIN_PASSWORD --adminemail="{admin_email}"',
        )
        # activate "Boost Union" theme
        self._run_local_php_script(
            "admin/cli/cfg.php",
            "--name=theme --set=boost_union",
        )

    def _extract_from_env(self, var_name: str) -> str:
        return subprocess.run(
            [f". ./.env && echo ${var_name}"],
            cwd=self.path,
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _run_local_php_script(self, script: str, args: str) -> None:
        self._run_docker_command(f"exec webserver php {script} {args}")

    def _run_docker_command(self, action: str) -> None:
        result = subprocess.run(
            [self._build_command(action)], cwd=self.path, shell=True
        )
        log().info(result)

    def _build_command(self, action: str) -> str:
        return f". ./.env && {self.compose_script} {action}"
