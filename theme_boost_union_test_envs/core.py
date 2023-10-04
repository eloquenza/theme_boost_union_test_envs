from .cross_cutting import config, log
from .domain import (
    GitReference,
    GitRepository,
    MoodleCache,
    Testbed,
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
        pass

    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        pass

    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        pass

    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        pass
