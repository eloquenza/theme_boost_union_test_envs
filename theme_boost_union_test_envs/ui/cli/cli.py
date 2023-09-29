import sys
from typing import Any

import fire

from ...core import BoostUnionTestEnvCore
from ...cross_cutting import log
from ...domain.git import GitReference, GitReferenceType
from ...exceptions import (
    InfrastructureDoesNotExistYetError,
    NameAlreadyTakenError,
    VersionArgumentNeededError,
)


class BoostUnionTestEnvCLI:
    """BoostUnionTestEnvCLI capsulates all possible commands to provide a CLI. While it is not needed to be in a single class, we still want to do so, even it's just for making sure we are not shadowing python built-ins (see help)."""

    def __init__(self, core: BoostUnionTestEnvCore) -> None:
        self.core = core

    def init(
        self, infrastructure_name: str, gitreftype: str, gitrefname: str | int
    ) -> None:
        try:
            if not any([t in gitreftype for t in GitReferenceType]):
                raise fire.core.FireError(
                    "The 2nd argument needs to be either commit, branch or pr"
                )
            git_ref = GitReference(gitrefname, GitReferenceType(gitreftype))
            self.core.initialize_infrastructure(infrastructure_name, git_ref)
        except NameAlreadyTakenError as e:
            raise fire.core.FireError(
                "Your chosen name for the test infrastructure already exists, please choose a different one"
            ) from e

    def build(self, infrastructure_name: str, *versions: str) -> None:
        try:
            self.core.build_infrastructure(infrastructure_name, *versions)
        except VersionArgumentNeededError as e:
            raise fire.core.FireError("Please pass atleast one version") from e
        except InfrastructureDoesNotExistYetError as e:
            raise fire.core.FireError(
                "The infrastructure you have given does not exist, please check the spelling"
            ) from e

    def start(self, infrastructure_name: str, *versions: str) -> None:
        self.core.start_environment(infrastructure_name, *versions)

    def restart(self, infrastructure_name: str, *versions: str) -> None:
        self.core.restart_environment(infrastructure_name, *versions)

    def stop(self, infrastructure_name: str, *versions: str) -> None:
        self.core.stop_environment(infrastructure_name, *versions)

    def destroy(self, infrastructure_name: str, *versions: str) -> None:
        self.core.destroy_environment(infrastructure_name, *versions)

    def teardown(self, infrastructure_name: str) -> None:
        self.core.teardown_infrastructure(infrastructure_name)

    def help(self) -> None:
        print("theme_boost_union_test_envs")
        print("=" * len("theme_boost_union_test_envs"))
        print('Test environments for the Moodle theme "Boost Union"')


def configure_cli_logger() -> None:
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
    log().configure(**config)


def cli_main(core: BoostUnionTestEnvCore) -> None:
    configure_cli_logger()
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
        },
    )
