from typing import Callable

from .cross_cutting import config, log
from .domain import (
    GitReference,
    GitRepository,
    MoodleCache,
    Testbed,
    TestContainer,
    TestInfrastructure,
)
from .exceptions import InfrastructureDoesNotExistYetError, NameAlreadyTakenError


class BoostUnionTestEnvCore:
    def __init__(
        self,
        moodle_docker_repo: GitRepository,
        boost_union_repo: GitRepository,
        moodle_cache: MoodleCache,
    ) -> None:
        self.moodle_docker_repo = moodle_docker_repo
        self.boost_union_repo = boost_union_repo
        self.moodle_cache = moodle_cache

    def init_testbed(self) -> None:
        new_testbed = Testbed(self.moodle_docker_repo, self.moodle_cache.directory)
        new_testbed.init()

    def setup_infrastructure(
        self, infrastructure_name: str, git_ref: GitReference
    ) -> None:
        path = config().working_dir / infrastructure_name
        if path.exists():
            raise NameAlreadyTakenError("Infrastructure exists already")
        new_infra = TestInfrastructure(path, self.boost_union_repo, self.moodle_cache)
        new_infra.setup(git_ref)

    def build_infrastructure(self, infrastructure_name: str, *versions: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        existing_infra = TestInfrastructure(
            path, self.boost_union_repo, self.moodle_cache
        )
        existing_infra.build(*versions)

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

    def start_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.start,
            TestContainer.start.__name__,
            *versions,
        )

    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.stop,
            TestContainer.stop.__name__,
            *versions,
        )

    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.restart,
            TestContainer.restart.__name__,
            *versions,
        )

    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        self._container_call_helper(
            infrastructure_name,
            TestContainer.destroy,
            TestContainer.destroy.__name__,
            *versions,
        )

    def _container_call_helper(
        self,
        infrastructure_name: str,
        function: Callable[[TestContainer], None],
        action: str,
        *versions: str,
    ) -> None:
        infrastructure_path = config().working_dir / infrastructure_name
        if not infrastructure_path.exists():
            raise InfrastructureDoesNotExistYetError()
        log().info(f"{action} envs for the following versions:")
        if not versions:
            log().info(f"{action}ing all existing envs")
            # TODO: return all available versions to start these
        for ver in versions:
            log().info(f"* {ver}")
        for ver in versions:
            # TODO: check if version actually exists
            path = infrastructure_path / "moodles" / ver
            log().info(f"{action}ing container for moodle {path.name}")
            function(TestContainer(path))
            log().info(f"done {action}ing container")
