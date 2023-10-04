import sys
from typing import Any

import fire

from ...core import BoostUnionTestEnvCore
from ...cross_cutting import log
from ...domain.git import GitReference, GitReferenceType
from ...exceptions import (
    InfrastructureDoesNotExistYetError,
    InvalidMoodleVersionError,
    NameAlreadyTakenError,
    VersionArgumentNeededError,
)


class BoostUnionTestEnvCLI:
    """BoostUnionTestEnvCLI capsulates all possible commands to provide a CLI.While it is not needed to be in a single class, we still want to do so, even
    it's just for making sure we are not shadowing python built-ins (see help).
    """

    def __init__(self, core: BoostUnionTestEnvCore) -> None:
        self.core = core

    def init(self) -> None:
        self.core.init_testbed()

    def setup(
        self, infrastructure_name: str, git_ref_type: str, git_ref_name: str | int
    ) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
            git_ref_type (str): _description_
            git_ref_name (str | int): _description_

        Raises:
            fire.core.FireError: _description_
            fire.core.FireError: _description_
        """
        try:
            if not any([t in git_ref_type for t in GitReferenceType]):
                raise fire.core.FireError(
                    "The 2nd argument needs to be either commit, branch or pr"
                )
            git_ref = GitReference(git_ref_name, GitReferenceType(git_ref_type))
            self.core.setup_infrastructure(infrastructure_name, git_ref)
        except NameAlreadyTakenError as e:
            raise fire.core.FireError(
                "Your chosen name for the test infrastructure already exists, please choose a different one"
            ) from e

    def build(self, infrastructure_name: str, *versions: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_

        Raises:
            fire.core.FireError: _description_
            fire.core.FireError: _description_
        """
        try:
            self.core.build_infrastructure(infrastructure_name, *versions)
        except VersionArgumentNeededError as e:
            raise fire.core.FireError("Please pass atleast one version") from e
        except InfrastructureDoesNotExistYetError as e:
            raise fire.core.FireError(
                "The infrastructure you have given does not exist, please check the spelling"
            ) from e
        except InvalidMoodleVersionError as e:
            raise fire.core.FireError(
                f"Moodle version {e.version} is invalid, please check if you wrote the correct one."
            ) from e

    def start(self, infrastructure_name: str, *versions: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
        """
        self.core.start_environment(infrastructure_name, *versions)

    def restart(self, infrastructure_name: str, *versions: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
        """
        self.core.restart_environment(infrastructure_name, *versions)

    def stop(self, infrastructure_name: str, *versions: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
        """
        self.core.stop_environment(infrastructure_name, *versions)

    def destroy(self, infrastructure_name: str, *versions: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
        """
        self.core.destroy_environment(infrastructure_name, *versions)

    def teardown(self, infrastructure_name: str) -> None:
        """_summary_

        Args:
            infrastructure_name (str): _description_
        """
        self.core.teardown_infrastructure(infrastructure_name)


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
            "init": cli.init,
            "setup": cli.setup,
            "build": cli.build,
            "start": cli.start,
            "restart": cli.restart,
            "stop": cli.stop,
            "destroy": cli.destroy,
            "teardown": cli.teardown,
        },
    )
