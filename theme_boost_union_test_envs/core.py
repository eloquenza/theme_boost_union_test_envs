from .cross_cutting import config, log
from .domain.git import GitReference
from .exceptions import InfrastructureDoesNotExistYetError
from .services import TestContainerService, TestInfrastructureService


class BoostUnionTestEnvCore:
    def __init__(
        self,
        container_service: TestContainerService,
        infrastructure_service: TestInfrastructureService,
    ) -> None:
        self.container_service = container_service
        self.infrastructure = infrastructure_service

    def initialize_infrastructure(
        self, infrastructure_name: str, git_ref: GitReference
    ) -> None:
        self.infrastructure.initialize(infrastructure_name, git_ref)

    def build_infrastructure(self, infrastructure_name: str, *versions: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        self.infrastructure.build(path, *versions)

    def teardown_infrastructure(self, infrastructure_name: str) -> None:
        # TODO: check if container are running, stop them first
        # TODO: then call docker remove to delete the images
        self.infrastructure.teardown(infrastructure_name)

    def start_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.container_service.start(infrastructure_name, *versions)

    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.container_service.stop(infrastructure_name, *versions)

    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.container_service.restart(infrastructure_name, *versions)

    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.container_service.destroy(infrastructure_name, *versions)
