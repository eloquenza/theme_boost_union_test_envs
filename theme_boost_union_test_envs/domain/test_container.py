import subprocess
from pathlib import Path

from ..cross_cutting import log


class TestContainer:
    def __init__(self, compose_file_path: Path) -> None:
        self.path = compose_file_path
        self.compose_script = "bin/moodle-docker-compose"

    def create(self) -> None:
        self._run_docker_command("create")

    def start(self) -> None:
        self._run_docker_command("up -d")
        self._configure_manual_testing()
        self._print_admin_pw()
        # TODO: for each ver:
        # TODO:   call docker compose start
        # TODO:   check if services really started
        # TODO:   post urls in console

    def restart(self) -> None:
        self._run_docker_command("restart")
        # TODO: for each ver: - maybe implement via stop and start here?
        # TODO:   call docker compose stop
        # TODO:   call docker compose start

    def stop(self) -> None:
        self._run_docker_command("stop")
        # TODO: for each ver:
        # TODO:   call docker compose stop
        # TODO:   make sure the services stopped gracefully
        # TODO:   list all URLs that are not available anymore?

    def destroy(self) -> None:
        self._run_docker_command("down")
        # TODO: for each ver:
        # TODO:   make sure containers are stopped
        # TODO:   else ask user to stop the container
        # TODO:   call docker compose rm?
        # TODO:   make sure command went well
        # TODO:   print out which containers are still running, so user knows what they need to stop

    def _print_admin_pw(self) -> None:
        log().info("Log in as admin with the following password:")
        subprocess.run(
            [". ./.env && echo $MOODLE_ADMIN_PASSWORD"], cwd=self.path, shell=True
        )

    def _configure_manual_testing(self) -> None:
        admin_email = "admin@example.com"
        short_name = "Moodle"
        full_name = "Docker'd Moodle"
        summary = f"Docker'd Moodle {self.path.name}"
        self._run_docker_command(
            f'exec webserver php admin/cli/install_database.php --agree-license --fullname="{full_name}" --shortname="{short_name}" --summary="{summary}" --adminpass=$MOODLE_ADMIN_PASSWORD --adminemail="{admin_email}"'
        )

    def _run_docker_command(self, action: str) -> None:
        result = subprocess.run(
            [self._build_command(action)], cwd=self.path, shell=True
        )
        log().info(result)

    def _build_command(self, action: str) -> str:
        return f". ./.env && {self.compose_script} {action}"
