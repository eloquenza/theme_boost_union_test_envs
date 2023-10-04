from enum import Enum

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .core import BoostUnionTestEnvCore
from .cross_cutting import ApplicationConfigManager, ApplicationLogger, TemplateEngine
from .domain import GitRepository, MoodleCache, MoodleDownloader
from .ui import cli_main, gui_main


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
    )

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
