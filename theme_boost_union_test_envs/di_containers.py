from dependency_injector import containers, providers
from loguru import logger

from .adapters import GitAdapter
from .core import BoostUnionTestEnvCore
from .services import TestContainerService, TestInfrastructureService
from .utils import ApplicationConfigManager


class Adapters(containers.DeclarativeContainer):

    config = providers.Configuration()

    git = providers.Factory(
        GitAdapter,
        config.git.boost_union_repo_url,
    )


class Services(containers.DeclarativeContainer):

    adapters = providers.DependenciesContainer()

    infrastructure = providers.Factory(
        TestInfrastructureService,
        git=adapters.git,
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

    services = providers.Container(
        Services,
        adapters=adapters,
    )
