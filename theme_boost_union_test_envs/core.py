from .services import TestContainerService, TestInfrastructureService
from .utils.dataclasses import GitReference


class BoostUnionTestEnvCore:
    def __init__(
        self,
        containerService: TestContainerService,
        infraService: TestInfrastructureService,
    ) -> None:
        self.containerService = containerService
        self.infraService = infraService

    def initialize_infrastructure(self, name: str, git_ref: GitReference) -> None:
        self.infraService.initialize(name, git_ref)

    def build_infrastructure(self, *versions: list[str]) -> None:
        self.infraService.build(*versions)

    def teardown_infrastructure(self, name: str) -> None:
        # check if container are running, stop them first
        # then call docker remove to delete the images
        self.infraService.teardown(name)

    def start_environment(self, *versions: list[str]) -> None:
        self.containerService.start(*versions)

    def stop_environment(self, *versions: list[str]) -> None:
        self.containerService.stop(*versions)

    def restart_environment(self, *versions: list[str]) -> None:
        self.containerService.restart(*versions)

    def destroy_environment(self, *versions: list[str]) -> None:
        self.containerService.destroy(*versions)