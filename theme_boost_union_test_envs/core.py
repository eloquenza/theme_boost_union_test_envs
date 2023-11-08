import functools
import pprint
from pathlib import Path
from typing import Any, Callable

from .cross_cutting import (
    InfrastructureYAMLParser,
    TemplateEngine,
    config,
    log,
    template_engine,
    yaml_parser,
)
from .domain import (
    GitReference,
    GitRepository,
    MoodleCache,
    Testbed,
    TestContainer,
    TestInfrastructure,
)
from .exceptions import (
    InfrastructureDoesNotExistYetError,
    NameAlreadyTakenError,
    TestbedDoesNotExistYetError,
)


def recreate_overview_html(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper_decorator(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        value = func(*args, **kwargs)
        # make sure the html page is updated after each command
        infrastructure_yaml = yaml_parser().load_testbed_info()
        template_engine().test_environment_overview_html(
            {"infrastructures": infrastructure_yaml}
        )
        return value

    return wrapper_decorator


class BoostUnionTestEnvCore:
    def __init__(
        self,
        moodle_docker_repo: GitRepository,
        boost_union_repo: GitRepository,
        moodle_cache: MoodleCache,
        yaml_parser: InfrastructureYAMLParser,
        template_engine: TemplateEngine,
    ) -> None:
        self.moodle_docker_repo = moodle_docker_repo
        self.boost_union_repo = boost_union_repo
        self.moodle_cache = moodle_cache
        self.yaml_parser = yaml_parser
        self.template_engine = template_engine

    @recreate_overview_html
    def init_testbed(self) -> None:
        new_testbed = Testbed(self.moodle_docker_repo, self.moodle_cache.directory)
        new_testbed.init()

    @recreate_overview_html
    def list_infrastructures(self) -> None:
        # should probably be encapsulated in another business service
        if not config().working_dir.exists():
            raise TestbedDoesNotExistYetError
        infrastructures = self.yaml_parser.load_testbed_info()
        if not infrastructures:
            log().info("No infrastructure exists yet")
        else:
            # pretty-print dict
            pretty_infras = pprint.PrettyPrinter(depth=4).pformat(infrastructures)
            log().info(f"Listing all infrastructures: \n{pretty_infras}")

    @recreate_overview_html
    def setup_infrastructure(
        self, infrastructure_name: str, git_ref: GitReference
    ) -> None:
        path = config().working_dir / infrastructure_name
        if path.exists():
            raise NameAlreadyTakenError("Infrastructure exists already")
        new_infra = TestInfrastructure(path, self.boost_union_repo, self.moodle_cache)
        new_infra.setup(git_ref)
        # TODO: add infrastructure name + gitref to listing page
        self.yaml_parser.add_infrastructure(
            {
                infrastructure_name: {
                    "git_ref": {"type": git_ref.type.name, "reference": git_ref.ref},
                    "moodles": {},
                }
            }
        )

    @recreate_overview_html
    def build_infrastructure(self, infrastructure_name: str, *versions: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        existing_infra = TestInfrastructure(
            path, self.boost_union_repo, self.moodle_cache
        )
        built_moodles = existing_infra.build(*versions)
        # TODO: add new moodle test env to test infrastructure to listing page
        self.yaml_parser.add_infrastructure(
            {infrastructure_name: {"moodles": built_moodles}}
        )

    @recreate_overview_html
    def teardown_infrastructure(self, infrastructure_name: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        existing_infra = TestInfrastructure(
            path, self.boost_union_repo, self.moodle_cache
        )
        # TODO: check if container are running, stop them first
        # TODO: then call docker remove to delete the images
        existing_infra.teardown(infrastructure_name)
        # TODO: remove infrastructure from listing page
        self.yaml_parser.remove_infrastructure(infrastructure_name)

    @recreate_overview_html
    def start_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.start,
            *versions,
        )
        self.yaml_parser.add_infrastructure(
            {
                infrastructure_name: {
                    "moodles": {
                        ver: {
                            "status": "STARTED",
                        }
                        for ver in versions
                    }
                }
            }
        )

    @recreate_overview_html
    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.stop,
            *versions,
        )
        self.yaml_parser.add_infrastructure(
            {
                infrastructure_name: {
                    "moodles": {
                        ver: {
                            "status": "STOPPED",
                        }
                        for ver in versions
                    }
                }
            }
        )

    @recreate_overview_html
    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.restart,
            *versions,
        )

    @recreate_overview_html
    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.destroy,
            *versions,
        )
        for ver in versions:
            self.yaml_parser.remove_moodle(infrastructure_name, ver)

    def _container_call_helper(
        self,
        infrastructure_name: str,
        function: Callable[[TestContainer], None],
        *versions: str,
    ) -> None:
        infrastructure_path = config().working_dir / infrastructure_name
        if not infrastructure_path.exists():
            raise InfrastructureDoesNotExistYetError()
        action = function.__name__
        log().info(f"{action} envs for the following versions:")
        if not versions:
            log().info(f"{action}ing all existing envs")
            # TODO: return all available versions to start these
        for ver in versions:
            log().info(f"* {ver}")
        for ver in versions:
            path = infrastructure_path / "moodles" / ver
            log().info(f"{action}ing container for moodle {path.name}")
            function(TestContainer(path))
            log().info(f"done {action}ing container")
