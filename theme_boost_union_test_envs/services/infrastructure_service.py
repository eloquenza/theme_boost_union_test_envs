from loguru import logger


class TestInfrastructureService:
    def __init__(self) -> None:
        pass

    def initialize(self, name: str, commit: str) -> None:
        logger.info(f"init test named {name} from commit {commit} in folder ./{name}")

    def build(self, *versions: list[str]) -> None:
        if not versions:
            raise ValueError
        logger.info("build envs for the following versions:")
        for ver in versions:
            logger.info(f"* {ver}")

    def teardown(self, name: str) -> None:
        logger.info(f"teardown test bed of {name}")
