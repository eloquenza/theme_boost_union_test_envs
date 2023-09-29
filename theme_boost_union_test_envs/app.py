from enum import Enum

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .adapters import GitAdapter
from .core import BoostUnionTestEnvCore
from .cross_cutting import ApplicationConfigManager, ApplicationLogger
from .domain import MoodleCache
from .services import TestContainerService, TestInfrastructureService
from .ui import cli_main, gui_main


class Adapters(containers.DeclarativeContainer):

    config = providers.Configuration()

    git = providers.Factory(
        GitAdapter,
        repo_url=config.git.boost_union_repo_url,
    )


class Domain(containers.DeclarativeContainer):

    config = providers.Configuration()

    moodle_cache = providers.Factory(
        MoodleCache,
        cache_dir=config.moodle.cache_dir,
        download_url=config.moodle.source_url,
    )


class Services(containers.DeclarativeContainer):

    adapters = providers.DependenciesContainer()
    domain = providers.DependenciesContainer()

    infrastructure = providers.Factory(
        TestInfrastructureService,
        git=adapters.git,
        moodle_cache=domain.moodle_cache,
    )

    test_container = providers.Factory(
        TestContainerService,
    )


class CrossCuttingConcerns(containers.DeclarativeContainer):

    config = providers.Configuration()

    config_manager = providers.Singleton(
        ApplicationConfigManager,
        config=config,
    )

    log = providers.Singleton(ApplicationLogger)


class Application(containers.DeclarativeContainer):

    config = providers.Configuration(yaml_files=["config.yml"])

    cross_cutting_concerns = providers.Container(CrossCuttingConcerns, config=config)

    adapters = providers.Container(
        Adapters,
        config=config.adapters,
    )

    domain = providers.Container(Domain, config=config.core)

    services = providers.Container(
        Services,
        adapters=adapters,
        domain=domain,
    )

    core = providers.Singleton(
        BoostUnionTestEnvCore,
        container_service=services.test_container,
        infrastructure_service=services.infrastructure,
    )


class UserInterface(str, Enum):
    CLI = "cli"
    GUI = "gui"


def main(
    interface_choice: UserInterface,
) -> int:
    app = Application()
    app.wire(packages=["theme_boost_union_test_envs"])
    _spawn_interface(interface_choice)
    return 0


@inject
def _spawn_interface(
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
