from enum import Enum

from dependency_injector.wiring import Provide, inject

from .core import BoostUnionTestEnvCore
from .di_containers import Application
from .ui import cli_main, gui_main


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
    core: BoostUnionTestEnvCore = Provide[Application.core],
) -> None:
    if interface_choice == UserInterface.CLI:
        cli_main(core)
    elif interface_choice == UserInterface.GUI:
        gui_main(core)
    else:
        valid_interfaces = [f"UserInterface.{e.value.upper()}" for e in UserInterface]
        raise ValueError(
            f"Please provide a valid ({valid_interfaces}) interface argument"
        )
