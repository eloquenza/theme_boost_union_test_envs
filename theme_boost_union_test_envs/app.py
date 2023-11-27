import sys
from enum import Enum
from pathlib import Path

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .core import BoostUnionTestEnvCore
from .cross_cutting import (
    ApplicationConfigManager,
    ApplicationLogger,
    InfrastructureYAMLParser,
    TemplateEngine,
)
from .domain import GitRepository, MoodleCache, MoodleDownloader
from .exceptions import BoostUnionTestEnvValueError
from .ui import cli_main, gui_main

# The classes "Adapters", "Domain", "CrossCuttingConcerns" and "Application" are simply containers that utilize dependency injection to make sure that all the correct classes are mapped to mandatory variables in the constructors.


class Adapters(containers.DeclarativeContainer):

    config = providers.Configuration()

    moodle_downloader = providers.Singleton(
        MoodleDownloader,
        url=config.moodle.downloader.url,
        retries=config.moodle.downloader.retries,
        retry_timeout=config.moodle.downloader.retries,
    )


class Domain(containers.DeclarativeContainer):

    adapters = providers.DependenciesContainer()

    moodle_cache = providers.Singleton(
        MoodleCache,
        downloader=adapters.moodle_downloader,
    )


class CrossCuttingConcerns(containers.DeclarativeContainer):

    config = providers.Configuration()
    moodle_versions_to_php_versions = providers.Configuration(
        yaml_files=["moodle-versions-to-supported-php-versions.yaml"]
    )

    config_manager = providers.Singleton(
        ApplicationConfigManager,
        config=config,
        # only wiring chosen environment config as path here, because
        # pre-injection it's not possible to use 'config.environment' as
        # argument to read from another config file
        environment_file=config.environment.as_(lambda p: Path(sys.path[0]) / p),
        moodle_versions_to_php_versions=moodle_versions_to_php_versions,
    )

    infrastructure_yaml_parser = providers.Singleton(InfrastructureYAMLParser)
    log = providers.Singleton(ApplicationLogger)
    template_engine = providers.Singleton(TemplateEngine)


class Application(containers.DeclarativeContainer):

    config = providers.Configuration(yaml_files=["config.yml"])

    cross_cutting_concerns = providers.Container(
        CrossCuttingConcerns,
        config=config,
    )

    adapters = providers.Container(
        Adapters,
        config=config.adapters,
    )

    domain = providers.Container(
        Domain,
        adapters=adapters,
    )

    core = providers.Singleton(
        BoostUnionTestEnvCore,
        yaml_parser=cross_cutting_concerns.infrastructure_yaml_parser,
        template_engine=cross_cutting_concerns.template_engine,
    )


class UserInterface(str, Enum):
    CLI = "cli"
    GUI = "gui"


def main(
    interface_choice: UserInterface,
) -> int:
    app = Application()
    # This starts the wiring for our DI library by providing it the package from which the required classes should come from
    app.wire(packages=["theme_boost_union_test_envs"])
    _spawn_interface(interface_choice)
    return 0


# DI begins here via the decorator
@inject
def _spawn_interface(
    interface_choice: UserInterface,
    core: BoostUnionTestEnvCore = Provide[Application.core],
) -> None:
    """Spawns the chosen interface and gives control to said interface.

    Args:
        interface_choice (UserInterface): A value from the UserInterface enum, that decides which interface will be spawned. Valid values: CLI or GUI.
        core (BoostUnionTestEnvCore, optional): Injected core object. Defaults to Provide[Application.core].

    Raises:
        BoostUnionTestEnvValueError: raised if an invalid interface choice has been made
    """
    if interface_choice == UserInterface.CLI:
        cli_main(core)
    elif interface_choice == UserInterface.GUI:
        gui_main(core)
    else:
        valid_interfaces = [f"UserInterface.{e.value.upper()}" for e in UserInterface]
        raise BoostUnionTestEnvValueError(
            f"Please provide a valid ({valid_interfaces}) interface argument"
        )
