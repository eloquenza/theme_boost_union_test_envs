from dependency_injector import containers, providers
from loguru import logger

from .adapters import GitAdapter
from .core import BoostUnionTestEnvCore
from .domain import MoodleCache
from .services import TestContainerService, TestInfrastructureService
from .utils import ApplicationConfigManager


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
        containerService=services.test_container,
        infraService=services.infrastructure,
    )
