from loguru import logger


class TestContainerService:
    def __init__(self) -> None:
        pass

    def start(self, *versions: list[str]) -> None:
        self.__helper("start", *versions)
        # for each ver:
        #   call docker compose start
        #   check if services really started
        #   post urls in console

    def restart(self, *versions: list[str]) -> None:
        self.__helper("restart", *versions)
        # for each ver: - maybe implement via stop and start here?
        #   call docker compose stop
        #   call docker compose start

    def stop(self, *versions: list[str]) -> None:
        self.__helper("stop", *versions)
        # for each ver:
        #   call docker compose stop
        #   make sure the services stopped gracefully
        #   list all URLs that are not available anymore?

    def destroy(self, *versions: list[str]) -> None:
        self.__helper("destroy", *versions)
        # for each ver:
        #   make sure containers are stopped
        #   else ask user to stop the container
        #   call docker compose rm?
        #   make sure command went well
        #   print out which containers are still running, so user knows what they need to stop

    def __helper(self, action: str, *versions: list[str]) -> None:
        logger.info(f"{action} envs for the following versions:")
        if not versions:
            logger.info(f"{action}ing all existing envs")
        for ver in versions:
            logger.info(f"* {ver}")
