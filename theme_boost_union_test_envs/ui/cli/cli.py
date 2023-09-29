import sys
from typing import Any

import fire

from ...core import BoostUnionTestEnvCore
from ...cross_cutting import log
from ...domain.git import GitReference, GitReferenceType
from ...exceptions import NameAlreadyTakenError, VersionArgumentNeededError


class BoostUnionTestEnvCLI:
    """BoostUnionTestEnvCLI capsulates all possible commands to provide a CLI. While it is not needed to be in a single class, we still want to do so, even it's just for making sure we are not shadowing python built-ins (see help)."""

    def __init__(self, core: BoostUnionTestEnvCore) -> None:
        self.core = core

    def init(
        self,
        name: str,
        commit: str | None = None,
        branch: str | None = None,
        pr: int | None = None,
    ) -> None:
        try:
            if not commit and not branch and not pr:
                raise fire.core.FireError(
                    "This command requires to be passed either a commit, a branch name or a PR number"
                )
            if commit:
                git_ref = GitReference(commit, GitReferenceType.COMMIT)
            elif branch:
                git_ref = GitReference(branch, GitReferenceType.BRANCH)
            elif pr:
                git_ref = GitReference(pr, GitReferenceType.PULL_REQUEST)
            self.core.initialize_infrastructure(name, git_ref)
        except NameAlreadyTakenError as e:
            raise fire.core.FireError(
                "Your chosen name for the test infrastructure already exists, please choose a different one"
            ) from e

    def build(self, *versions: str) -> None:
        try:
            self.core.build_infrastructure(*versions)
        except VersionArgumentNeededError as e:
            raise fire.core.FireError("Please pass atleast one version") from e

    def start(self, *versions: str) -> None:
        self.core.start_environment(*versions)

    def restart(self, *versions: str) -> None:
        self.core.restart_environment(*versions)

    def stop(self, *versions: str) -> None:
        self.core.stop_environment(*versions)

    def destroy(self, *versions: str) -> None:
        self.core.destroy_environment(*versions)

    def teardown(self, name: str) -> None:
        self.core.teardown_infrastructure(name)

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
