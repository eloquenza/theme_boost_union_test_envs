from loguru import logger


class TestContainerService:
    def __init__(self) -> None:
        pass

    def start(self, *versions: list[str]) -> None:
        self.__helper("start", *versions)

    def restart(self, *versions: list[str]) -> None:
        self.__helper("restart", *versions)

    def stop(self, *versions: list[str]) -> None:
        self.__helper("stop", *versions)

    def destroy(self, *versions: list[str]) -> None:
        self.__helper("destroy", *versions)

    def __helper(self, action: str, *versions: list[str]) -> None:
        logger.info(f"{action} envs for the following versions:")
        if not versions:
            logger.info(f"{action}ing all existing envs")
        for ver in versions:
            logger.info(f"* {ver}")
