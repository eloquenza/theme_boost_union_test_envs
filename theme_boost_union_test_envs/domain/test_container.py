import shutil
import subprocess
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from ..cross_cutting import config, log, template_engine
from ..exceptions import MoodleTestEnvironmentDoesNotExistYetError


class TestContainer:
    def __init__(self, container_path: Path) -> None:
        # TODO: check if path exists
        self.path = container_path
        self.version = self.path.name
        # TODO: explain why parent.parent; specify path
        self.infrastructure = self.path.parent.parent.name
        self.compose_script = "bin/moodle-docker-compose"

    # ignoring types here for both function declarations as it is impossible to make this legal pythonese work with mypy
    # https://github.com/python/mypy/issues/7778
    # it also cannot be declared outside of this class due to a lack of forward declarations in this language
    # we would need to either be able to forward-declare TestContainer to make sure self can be type-hinted with TestContainer or hope python actually parses all available functions in side a file before executing it, so adding this decorator to the other methods doesn't fail with "not defined"
    def check_path_existence(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore
        """This decorator makes sure that the wrapped function will not be called if the path to the test container does not exist, i.e. the test container does not really exist.

        Args:
            func (Callable[..., Any]): the function that should be wrapped

        Raises:
            MoodleTestEnvironmentDoesNotExistYetError: raised if the test environment does not exist.

        Returns:
            Callable[..., Any]: the wrapped function
        """

        @wraps(func)
        def wrapper(self) -> Any:  # type: ignore
            if not self.path.exists():
                raise MoodleTestEnvironmentDoesNotExistYetError(self.path.name)
            retval = func(self)
            return retval

        return wrapper

    def create(self) -> None:
        """Spawns a sub-shell to call 'docker-compose create' on this container.
        This makes sure the containers are functional.
        Might be more modern to call "up --no-start".
        """
        self._run_docker_command("create")

    @check_path_existence
    def start(self) -> None:
        """Spawns a sub-shell to call 'docker-compose up -d' on this container.
        This starts the container. Furthermore, this function will call a script to wait until the DB has started, to make sure the services can be used properly when this function has executed successfully.
        """
        self._run_docker_command("up -d && bin/moodle-docker-wait-for-db")
        self._configure_manual_testing()
        host, port, pw, _ = self.get_access_info()
        log().info("Please access the created Moodle container here:")
        log().info(f"Enter the following URL into your browser: http://{host}:{port}/")
        log().info(f"Login as admin with pw: {pw}")

    @check_path_existence
    def restart(self) -> None:
        """Spawns a sub-shell to call 'docker-compose restart' on this container.
        This stops and then starts this container.
        """
        self._run_docker_command("restart")

    @check_path_existence
    def stop(self) -> None:
        """Spawns a sub-shell to call 'docker-compose stop' on this container.
        This stops the running container.
        """
        self._run_docker_command("stop")

    @check_path_existence
    def destroy(self) -> None:
        """Spawns a sub-shell to call 'docker-compose down' on this container.
        This optionally stops and then removes the container.
        """
        self._run_docker_command("down")
        nginx_conf = template_engine().create_moodle_nginx_conf_path(
            self.infrastructure, self.version
        )
        log().info(
            f"removing nginx configuration {nginx_conf} for container of {self.infrastructure}/{self.version}"
        )
        if nginx_conf.exists():
            nginx_conf.unlink()
        if self.path.exists():
            shutil.rmtree(self.path)

    @check_path_existence
    def get_access_info(self) -> tuple[str, str, str, str]:
        """Returns the host, port and admin's password needed to access it's test container.

        Returns:
            tuple[str, str, str]: host, port and admin's PW in a tuple.
        """
        www_host = self._extract_from_env("MOODLE_DOCKER_WEB_HOST")
        www_port = self._extract_from_env("MOODLE_DOCKER_WEB_PORT")
        admin_password = self._extract_from_env("MOODLE_ADMIN_PASSWORD")
        db_port = self._extract_from_env("MOODLE_DOCKER_DB_PORT")
        return (www_host, www_port, admin_password, db_port)

    def _configure_manual_testing(self) -> None:
        admin_email = "admin@example.com"
        # we do not actual care about concrete names here, so let's make it all the same; var naming is just kept for parity with CLI interface
        short_name = f"{self.infrastructure} - {self.version}"
        full_name = short_name
        summary = short_name
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
        """Extracts the value of the given variable name from the container's environment file.
        Might be slower due to it's implementation, as we spawn a sub-shell, source the .env and then echo the exported variables. It was the easiest way, and the "slowness" of this implemenation shouldn't matter.

        Args:
            var_name (str): name of the variable for which the value should be extracted

        Returns:
            str: extracted value
        """
        return subprocess.run(
            [f". ./.env && echo ${var_name}"],
            cwd=self.path,
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _run_local_php_script(self, script: str, args: str) -> None:
        """Runs a PHP script local to the webserver container, where Moodle is installed.

        Args:
            script (str): path and file name of the script that is to be run.
            args (str): arguments that should be passed to the script.
        """
        self._run_docker_command(f"exec webserver php {script} {args}")

    def _run_docker_command(self, action: str) -> None:
        """Runs a typical docker compose command via the script that is provided by the moodle-docker project.

        Args:
            action (str): a typical docker compose command that should be sent to the containers (up, down, stop, restart)
        """
        command = self._build_command(action)
        log().info(f"executing {command}")
        result = subprocess.run([command], cwd=self.path, shell=True)
        log().info(result)

    def _build_command(self, action: str) -> str:
        """Builds a string containing the command line that will be used in the sub-shell and returns it, by sourcing the environment file for this test container and afterwards calling into the script wrapping docker compose commands.

        Args:
            action (str): a typical docker compose command that should be sent to the containers (up, down, stop, restart)

        Returns:
            str: the string containing the command line
        """
        return f". ./.env && {self.compose_script} {action}"
