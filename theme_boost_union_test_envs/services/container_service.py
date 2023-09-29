from ..cross_cutting import log


class TestContainerService:
    def __init__(self) -> None:
        pass

    def start(self, *versions: str) -> None:
        self.__helper("start", *versions)
        # TODO: for each ver:
        # TODO:   call docker compose start
        # TODO:   check if services really started
        # TODO:   post urls in console

    def restart(self, *versions: str) -> None:
        self.__helper("restart", *versions)
        # TODO: for each ver: - maybe implement via stop and start here?
        # TODO:   call docker compose stop
        # TODO:   call docker compose start

    def stop(self, *versions: str) -> None:
        self.__helper("stop", *versions)
        # TODO: for each ver:
        # TODO:   call docker compose stop
        # TODO:   make sure the services stopped gracefully
        # TODO:   list all URLs that are not available anymore?

    def destroy(self, *versions: str) -> None:
        self.__helper("destroy", *versions)
        # TODO: for each ver:
        # TODO:   make sure containers are stopped
        # TODO:   else ask user to stop the container
        # TODO:   call docker compose rm?
        # TODO:   make sure command went well
        # TODO:   print out which containers are still running, so user knows what they need to stop

    def __helper(self, action: str, *versions: str) -> None:
        log().info(f"{action} envs for the following versions:")
        if not versions:
            log().info(f"{action}ing all existing envs")
        for ver in versions:
            log().info(f"* {ver}")
