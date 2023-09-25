from dependency_injector import containers, providers
from loguru import logger

from .adapters import GitAdapter
from .core import BoostUnionTestEnvCore
from .services import TestContainerService, TestInfrastructureService


class Adapters(containers.DeclarativeContainer):

    config = providers.Configuration()

    git = providers.Factory(GitAdapter, config.repo_url, config.working_dir)


class Services(containers.DeclarativeContainer):

    adapters = providers.DependenciesContainer()

    infrastructure = providers.Factory(TestInfrastructureService, git=adapters.git)

    test_container = providers.Factory(
        TestContainerService,
    )


class Application(containers.DeclarativeContainer):

    config = providers.Configuration(yaml_files=["config.yml"])

    adapters = providers.Container(
        Adapters,
        config=config.adapters,
    )

    services = providers.Container(
        Services,
        adapters=adapters,
    )
