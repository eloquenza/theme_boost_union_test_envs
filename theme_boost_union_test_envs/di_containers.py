from dependency_injector import containers, providers
from loguru import logger

from .core import BoostUnionTestEnvCore
from .services import TestContainerService, TestInfrastructureService


class Services(containers.DeclarativeContainer):

    infrastructure = providers.Factory(
        TestInfrastructureService,
    )

    test_container = providers.Factory(
        TestContainerService,
    )


class Application(containers.DeclarativeContainer):

    services = providers.Container(
        Services,
    )
