import sys
from typing import Any

import fire
from git import GitCommandError

from ...core import BoostUnionTestEnvCore
from ...cross_cutting import log
from ...domain.git import GitReference, GitReferenceType
from ...exceptions import (
    InfrastructureDoesNotExistYetError,
    InvalidMoodleVersionError,
    MoodleTestEnvironmentDoesNotExistYetError,
    NameAlreadyTakenError,
    TestbedDoesNotExistYetError,
    VersionArgumentNeededError,
)


class BoostUnionTestEnvCLI:
    """BoostUnionTestEnvCLI capsulates all possible business operations to provide a CLI.While it is not needed to be in a single class, we still want to do so, even it's just for making sure we are not shadowing python built-ins (see help)."""

    def __init__(self, core: BoostUnionTestEnvCore) -> None:
        self.core = core

    def list(self) -> None:
        try:
            self.core.list_infrastructures()
        except TestbedDoesNotExistYetError:
            raise fire.core.FireError(
                "No test infrastructure can be found as the test bed has not been initialized yet."
            )

    def init(self) -> None:
        """The 'init' command initializes the working directory configured in the 'config.yml'. This entails cloning HEAD of moodle-docker into it, creating a ".moodles/" subdirectory which is used as a local cache to for already downloaded Moodle versions.
        As this command is only needed once, ever, you can completely disregard this.
        """
        self.core.init_testbed()

    def setup(
        self, infrastructure_name: str, git_ref_type: str, git_ref_name: str | int
    ) -> None:
        """The 'setup' command creates a new test infrastructure for a given Boost Union "version". This entails creating a folder in the configured working directory with the given name, creating a subdirectory with the name "moodles", in which the files for the different Moodle containers will reside in, and a "theme" subdirectory, in which Boost Union will be cloned into. The "theme" subdirectory will be mounted into each Moodle container created later on.
        This is the first step needed to setup a new environment for manual testing.

        Args:
            infrastructure_name (str): Name the test infrastructure should have. Used for the identification of said infrastructure, as well as for it's folder in the configured working dir.
            git_ref_type (str): String which describes of which type the upcoming git reference will be. Valid values: "commit", "branch", "pr" or "tag"
            git_ref_name (str | int): A valid git reference of the "Boost Union" theme repository which will be used to clone said repository Valid values: A commit sha, a branch name, a pr number or a tag name.

        Raises:
            fire.core.FireError: An error describing that either the passed git reference type is invalid or that the name is already in use by another test infrastructure
        """
        try:
            if not any([git_ref_type in t for t in GitReferenceType]):
                raise fire.core.FireError(
                    "The 2nd argument needs to be either commit, branch, pr OR tag"
                )
            git_ref = GitReference(git_ref_name, GitReferenceType(git_ref_type))
            self.core.setup_infrastructure(infrastructure_name, git_ref)
        except GitCommandError:
            raise fire.core.FireError(
                "Given git reference does not exist; please check it's spelling"
            )
        except NameAlreadyTakenError as e:
            raise fire.core.FireError(
                "Your chosen name for the test infrastructure already exists, please choose a different one"
            ) from e

    def build(self, infrastructure_name: str, *versions: str) -> None:
        """The 'build' command is responsible for the creation of new Moodle test containers. For each given Moodle version string, a test container setup is created that will include Moodle in the given version, as well as setup said moodle to be used for manual testing. Per default, each Moodle instance is created completely fresh, with a PostgreSQL DB, Mailpit as a e-mail sink.
        The created Moodle instances can be found inside the infrastructure's "moodles" folder, in an subdirectory equally named to it's Moodle version, e.g.: $infrastructure_directory/moodles/$moodle_version.

        Args:
            infrastructure_name (str): Name the test infrastructure for which the Moodle test containers should be build for

        Raises:
            fire.core.FireError: Error that denotes that the given test infrastructure does not exist, or that either no version at all or an invalid Moodle version string was given
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
        """The 'start' command is used to start up the Moodle instances previously created. For the given test infrastructure, the Moodle container containing the corresponding version will be started if available. If no version strings are passed, every available Moodle instance will be started.

        Args:
            infrastructure_name (str): Name the test infrastructure for which the Moodle test containers should be started for
            *versions (str): Moodle versions that are going to be used to identify which Moodle containers should be started
        """
        try:
            self.core.start_environment(infrastructure_name, *versions)
        except MoodleTestEnvironmentDoesNotExistYetError as e:
            raise fire.core.FireError(
                f"No test environment available for Moodle version {e.version}"
            ) from e

    def restart(self, infrastructure_name: str, *versions: str) -> None:
        """The 'restart' command is used to reboot the Moodle instances previously created. For the given test infrastructure, the Moodle container containing the corresponding version will be restarted if available. If no version strings are passed, every available Moodle instance will be restarted.

        Args:
            infrastructure_name (str): Name the test infrastructure for which the Moodle test containers should be restarted for
            *versions (str): Moodle versions that are going to be used to identify which Moodle containers should be restarted
        """
        try:
            self.core.restart_environment(infrastructure_name, *versions)
        except MoodleTestEnvironmentDoesNotExistYetError as e:
            raise fire.core.FireError(
                f"No test environment available for Moodle version {e.version}"
            ) from e

    def stop(self, infrastructure_name: str, *versions: str) -> None:
        """The 'stop' command is used to stop the Moodle instances previously created. For the given test infrastructure, the Moodle container containing the corresponding version will be stopped if available. If no version strings are passed, every available Moodle instance will be stopped.

        Args:
            infrastructure_name (str): Name the test infrastructure for which the Moodle test containers should be stopped for
            *versions (str): Moodle versions that are going to be used to identify which Moodle containers should be stopped
        """
        try:
            self.core.stop_environment(infrastructure_name, *versions)
        except MoodleTestEnvironmentDoesNotExistYetError as e:
            raise fire.core.FireError(
                f"No test environment available for Moodle version {e.version}"
            ) from e

    def destroy(self, infrastructure_name: str, *versions: str) -> None:
        """The 'destroy' command is used to destroy the Moodle instances previously created. For the given test infrastructure, the Moodle container containing the corresponding version will be destroyed if available. If no version strings are passed, every available Moodle instance will be destroyed.

        Args:
            infrastructure_name (str): Name the test infrastructure for which the Moodle test containers should be destroyed for
            *versions (str): Moodle versions that are going to be used to identify which Moodle containers should be destroyed
        """
        try:
            self.core.destroy_environment(infrastructure_name, *versions)
        except MoodleTestEnvironmentDoesNotExistYetError as e:
            raise fire.core.FireError(
                f"No test environment available for Moodle version {e.version}"
            ) from e

    def teardown(self, infrastructure_name: str) -> None:
        """The 'teardown' command is used to tear down the test infrastructure identified by the passed name. This entailes stopping all Moodle containers pertaining to said infrastructure if available and started, deleted all docker related files for said containers and finally removing the checked out Boost Union repository itself.

        Args:
            infrastructure_name (str): Name of the infrastructure that should be torn down
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
    # Initializes the Fire library with the functions we wanna see in the CLI.
    fire.Fire(
        {
            # testbed related commands
            "init": cli.init,
            # test environment related commands
            "list": cli.list,
            "setup": cli.setup,
            "teardown": cli.teardown,
            # moodle container related commands
            "build": cli.build,
            "destroy": cli.destroy,
            "start": cli.start,
            "stop": cli.stop,
            "restart": cli.restart,
        },
    )
