import sys
from typing import Any

import fire
from dependency_injector.wiring import Provide, inject
from loguru import logger

from .core import BoostUnionTestEnvCore
from .di_containers import Application
from .services import TestContainerService, TestInfrastructureService

"""BoostUnionTestEnvCLI capsulates all possible commands to provide a CLI. While it is not needed to be in a single class, we still want to do so, even it's just for making sure we are not shadowing python built-ins (see help).
"""


class BoostUnionTestEnvCLI:
    def __init__(self, core: BoostUnionTestEnvCore) -> None:
        self.core = core

    def init(self, name: str, commit: str) -> None:
        self.core.initialize_infrastructure(name, commit)

    def build(self, *versions: list[str]) -> None:
        try:
            self.core.build_infrastructure(*versions)
        except ValueError as e:
            raise fire.core.FireError("Please pass atleast one version") from e

    def start(self, *versions: list[str]) -> None:
        self.core.start_environment(*versions)

    def restart(self, *versions: list[str]) -> None:
        self.core.restart_environment(*versions)

    def stop(self, *versions: list[str]) -> None:
        self.core.stop_environment(*versions)

    def destroy(self, *versions: list[str]) -> None:
        self.core.destroy_environment(*versions)

    def teardown(self, name: str) -> None:
        self.core.teardown_infrastructure(name)

    def help(self) -> None:
        print("theme_boost_union_test_envs")
        print("=" * len("theme_boost_union_test_envs"))
        print('Test environments for the Moodle theme "Boost Union"')


@inject
def main(
    infra_service: TestInfrastructureService = Provide[
        Application.services.infrastructure
    ],
    container_service: TestContainerService = Provide[
        Application.services.test_container
    ],
) -> None:
    config: dict[str, Any] = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DDTHH:mm:ss!UTC}</green> | {level} | <level>{message}</level>",
                "backtrace": True,
                "colorize": True,
                "diagnose": True,
            },
        ],
    }
    logger.configure(**config)
    core = BoostUnionTestEnvCore(container_service, infra_service)
    cli = BoostUnionTestEnvCLI(core)
    fire.Fire(
        {
            "help": cli.help,
            "init": cli.init,
            "build": cli.build,
            "start": cli.start,
            "restart": cli.restart,
            "stop": cli.stop,
            "destroy": cli.destroy,
            "teardown": cli.teardown,
        }
    )
