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

    config = providers.Configuration()

    adapters = providers.DependenciesContainer()

    moodle_cache = providers.Singleton(
        MoodleCache,
        cache_dir=config.core.moodle.cache.dir,
        downloader=adapters.moodle_downloader,
    )

    moodle_docker_repo = providers.Factory(
        GitRepository,
        repo_url=config.repos.moodle_docker.url,
        local_dir=config.repos.moodle_docker.dir,
    )

    boost_union_repo = providers.Factory(
        GitRepository,
        repo_url=config.repos.boost_union.url,
        local_dir=config.repos.boost_union.dir,
    )


class CrossCuttingConcerns(containers.DeclarativeContainer):

    config = providers.Configuration()

    config_manager = providers.Singleton(
        ApplicationConfigManager,
        config=config,
        # only wiring chosen environment config as path here, because
        # pre-injection it's not possible to use 'config.environment' as
        # argument to read from another config file
        environment_file=config.environment.as_(lambda p: Path(sys.path[0]) / p),
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
        config=config,
    )

    core = providers.Singleton(
        BoostUnionTestEnvCore,
        moodle_docker_repo=domain.moodle_docker_repo,
        boost_union_repo=domain.boost_union_repo,
        moodle_cache=domain.moodle_cache,
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
    # This starts the wiring for our DI library
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
