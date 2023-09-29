from .cross_cutting import config, log
from .domain.git import GitReference
from .exceptions import InfrastructureDoesNotExistYetError
from .services import TestContainerService, TestInfrastructureService


class BoostUnionTestEnvCore:
    def __init__(
        self,
        containerService: TestContainerService,
        infraService: TestInfrastructureService,
    ) -> None:
        self.containerService = containerService
        self.infraService = infraService

    def initialize_infrastructure(
        self, infrastructure_name: str, git_ref: GitReference
    ) -> None:
        self.infraService.initialize(infrastructure_name, git_ref)

    def build_infrastructure(self, infrastructure_name: str, *versions: str) -> None:
        path = config().working_dir / infrastructure_name
        if not path.exists():
            raise InfrastructureDoesNotExistYetError()
        self.infraService.build(path, *versions)

    def teardown_infrastructure(self, infrastructure_name: str) -> None:
        # TODO: check if container are running, stop them first
        # TODO: then call docker remove to delete the images
        self.infraService.teardown(infrastructure_name)

    def start_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.containerService.start(infrastructure_name, *versions)

    def stop_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.containerService.stop(infrastructure_name, *versions)

    def restart_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.containerService.restart(infrastructure_name, *versions)

    def destroy_environment(self, infrastructure_name: str, *versions: str) -> None:
        self.containerService.destroy(infrastructure_name, *versions)
