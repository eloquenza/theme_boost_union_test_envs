from enum import Enum

from dependency_injector.wiring import Provide, inject

from .cli import cli_main
from .core import BoostUnionTestEnvCore
from .di_containers import Application
from .services import TestContainerService, TestInfrastructureService


class UserInterface(str, Enum):
    CLI = "cli"
    GUI = "gui"


def main(
    interface_choice: UserInterface,
) -> int:
    app = Application()
    app.wire(packages=["theme_boost_union_test_envs"])
    spawn_interface(interface_choice)
    return 0


@inject
def spawn_interface(
    interface_choice: UserInterface,
    infra_service: TestInfrastructureService = Provide[
        Application.services.infrastructure
    ],
    container_service: TestContainerService = Provide[
        Application.services.test_container
    ],
) -> None:
    core = BoostUnionTestEnvCore(container_service, infra_service)
    if interface_choice == UserInterface.CLI:
        cli_main(core)
    elif interface_choice == UserInterface.GUI:
        raise ValueError("GUI is not yet implemented")
    else:
        raise ValueError("Please provide a valid interface argument")
