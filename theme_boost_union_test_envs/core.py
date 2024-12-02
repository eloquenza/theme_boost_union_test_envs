import functools
import subprocess
from collections import defaultdict
from pathlib import Path
from pprint import PrettyPrinter
from typing import Any, Callable

from .cross_cutting import (
    InfrastructureYAMLParser,
    TemplateEngine,
    config,
    log,
    template_engine,
    yaml_parser,
)
from .domain import Testbed, TestContainer, TestInfrastructure
from .entities import GitReference, MoodlePlugin
from .exceptions import (
    InfrastructureDoesNotExistYetError,
    NameAlreadyTakenError,
    TestbedDoesNotExistYetError,
)


def recreate_overview_html(func: Callable[..., Any]) -> Callable[..., Any]:
    """This decorator makes sure that after the wrapped function has been executed successfully, the static webpage displaying all available test environments will be updated.

    Args:
        func (Callable[..., Any]): a function that should be wrapped to make sure the static webpage is updated afterwards

    Returns:
        Callable[..., Any]: the wrapped function
    """

    @functools.wraps(func)
    def wrapper_decorator(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        # call the wrapped function with all passed args
        value = func(*args, **kwargs)
        # make sure the html page is updated after each command
        infrastructure_yaml = yaml_parser().load_testbed_info()
        # Using a defaultdict here to make sure the following operation doesn't result in a KeyError when adding keys for the first time
        envs_sorted_by_plugin = defaultdict(dict)
        for infra_name, info in infrastructure_yaml.items():
            envs_sorted_by_plugin[info["plugin"]] |= {infra_name: info}
        template_engine().test_environment_overview_html(
            {"infrastructures": envs_sorted_by_plugin}
        )
        return value

    return wrapper_decorator


def check_testbed_existence(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper_decorator(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        if not config().working_dir.exists():
            raise TestbedDoesNotExistYetError
        # call the wrapped function with all passed args
        value = func(*args, **kwargs)
        return value

    return wrapper_decorator


class BoostUnionTestEnvCore:
    def __init__(
        self,
        yaml_parser: InfrastructureYAMLParser,
        template_engine: TemplateEngine,
    ) -> None:
        self.yaml_parser = yaml_parser
        self.template_engine = template_engine

    @recreate_overview_html
    def init_testbed(self) -> None:
        new_testbed = Testbed()
        new_testbed.init()

    @recreate_overview_html
    @check_testbed_existence
    def list_infrastructures(self) -> None:
        # Reading infrastructure info from "yaml file database" and printing it
        infrastructures = self.yaml_parser.load_testbed_info()
        if not infrastructures:
            log().info("No infrastructure exists yet")
        else:
            # pretty-print dict
            pretty_infras = PrettyPrinter(depth=4).pformat(infrastructures)
            log().info(f"Listing all infrastructures: \n{pretty_infras}")

    @recreate_overview_html
    @check_testbed_existence
    def setup_infrastructure(
        self, infrastructure_name: str, plugin: MoodlePlugin, git_ref: GitReference
    ) -> None:
        path = config().working_dir / infrastructure_name
        if path.exists():
            raise NameAlreadyTakenError("Infrastructure exists already")
        new_infra = TestInfrastructure(path)
        new_infra.setup(plugin, git_ref)
        # Adding infrastructure name, plugin_name + gitref to file database
        self.yaml_parser.new_infrastructure(infrastructure_name, plugin, git_ref)

    @recreate_overview_html
    @check_testbed_existence
    def build_infrastructure(self, infrastructure_name: str, *versions: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        existing_infra = TestInfrastructure(path)
        built_moodles = existing_infra.build(*versions)
        # Adding new moodle environments in selected infrastructure to file database
        self.yaml_parser.add_moodles_to_infrastructure(
            infrastructure_name, built_moodles
        )
        if config().is_proxied:
            log().info(
                "restarting nginx, our proxy server; you will lose connection if you are logged in via web-browser"
            )
            # This looks dangerous, but isn't.
            # I require of the administrator to provide the user which runs this script to allow an exception solely for the restart of nginx.
            # This can be done by sudo visudo -f /etc/sudoers.d/allow-systemctl-for-boost-union-testing
            # and entering: $user ALL=NOPASSWD: /usr/bin/systemctl restart nginx
            # This "convoluted" idea came from a lazy perspective of not wanting to handle root privileges inside this programm.
            # This way, only the spawned subshell gains sudo rights; and also only specifically for a Nginx restart
            subprocess.run(["sudo systemctl restart nginx"], shell=True)
            # We are only restarting Nginx after a new test env has been added, as we want to reduce the amount of restarts.
            # Normally we should restart after removing a test environment too, but it shouldn't be harmful to leave Nginx running with a few flawed configs

    @recreate_overview_html
    @check_testbed_existence
    def teardown_infrastructure(self, infrastructure_name: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        existing_infra = TestInfrastructure(path)
        existing_infra.teardown()
        # Removing infrastructure from file database
        self.yaml_parser.remove_infrastructure(infrastructure_name)

    @recreate_overview_html
    def start_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.start,
            *versions,
        )
        # make sure the selected moodle test containers are listed as "STARTED" in the yaml DB
        self.yaml_parser.change_moodle_test_container_status(
            infrastructure_name, "STARTED", *versions
        )

    @recreate_overview_html
    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.stop,
            *versions,
        )
        # make sure the selected moodle test containers are listed as "STOPPED in the yaml DB
        self.yaml_parser.change_moodle_test_container_status(
            infrastructure_name, "STOPPED", *versions
        )

    @recreate_overview_html
    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.restart,
            *versions,
        )
        # TODO: should update yaml DB to STARTED? Would involve waiting until restart happened to make sure the right status is listed

    @recreate_overview_html
    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.destroy,
            *versions,
        )
        # make sure the moodle environment is removed from our "yaml database"
        for ver in versions:
            self.yaml_parser.remove_moodle(infrastructure_name, ver)

    @check_testbed_existence
    def _container_call_helper(
        self,
        infrastructure_name: str,
        function: Callable[[TestContainer], None],
        *versions: str,
    ) -> None:
        """Helper function to streamline the way our container functions operate. The only difference between our container functions is the action (start/up, stop, restart, destroy/down) we are issuing towards the containers. The logging and the 'algorithm' is otherwise the same.

        Args:
            infrastructure_name (str): the infrastructure for which the containers should be started for
            function (Callable[[TestContainer], None]): the action that should be issued to the containers (start/up, stop, restart, destroy/down)
            versions (tuple[str, ...]): moodle versions that decide which containers should be started

        Raises:
            InfrastructureDoesNotExistYetError: raised if the passed infrastructure doesn't exist, therefore no containers can exist
        """
        infrastructure_path = config().working_dir / infrastructure_name
        if not infrastructure_path.exists():
            raise InfrastructureDoesNotExistYetError()
        # use function name for logging as it describes perfectly what is going to happen
        action = function.__name__
        log().info(f"{action} envs for the following versions:")
        # if no version string has been passed, we want to issue the action to all available moodle test containers
        if not versions:
            log().info(f"{action}ing all existing envs")
            # TODO: return all available versions to start these
        for ver in versions:
            log().info(f"* {ver}")
        for ver in versions:
            path = infrastructure_path / "moodles" / ver
            log().info(f"{action}ing container for moodle {path.name}")
            # pythonic way to call a passed, higher-order class instance function on an newly created object
            function(TestContainer(path))
            log().info(f"done {action}ing container")
