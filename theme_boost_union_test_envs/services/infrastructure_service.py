from loguru import logger

from ..adapters import GitAdapter
from ..utils.config import get_config
from ..utils.dataclasses import GitReference


class TestInfrastructureService:
    def __init__(self, git: GitAdapter) -> None:
        self.git = git

    def initialize(
        self,
        name: str,
        git_ref: GitReference,
    ) -> None:
        logger.info(f"initializing new test infrastructure named '{name}'")
        try:
            self.git.clone_repo(name, git_ref)
            logger.info("done init - find your test infrastructure here:")
            logger.info(f"\tpath: {get_config().working_dir / name}")
        except ValueError as e:
            logger.error(f"{e}")
            raise e

    def build(self, *versions: list[str]) -> None:
        if not versions:
            raise ValueError
        logger.info("build envs for the following versions:")
        # mkdir moodles; skip if already existing
        for ver in versions:
            # check if ver already exists; continue then
            logger.info(f"* {ver}")
            # mkdir with ver as name
            # download moodle sources into each dir - https://github.com/moodle/moodle/archive/refs/tags/v4.2.2.zip
            # pull moodle-docker into it
            # replace all the params from moodle-docker with the correct ones:
            # * adjust the mounts in the docker-compose:
            #     * add theme mount
            #     * add moodle sources mount
            # * COMPOSE_NAME: given by init / folder_name
            # * MOODLE_WWW_PORT: 0.0.0.0:$empty_port
            # * NGINX_SERVER_NAME: see COMPOSE_NAME
            # * absolute path for Moodle source
            # * absolute path for "Boost Union" theme
            # * MOODLE_VER
            # * MOODLE_DOCKER_PHP_VERSION
        # moodles are cooked al-dente; enjoy

    def teardown(self, name: str) -> None:
        logger.info(f"teardown test bed of {name}")
        # then remove file from nginx; to make sure the moodles cannot be served anymore
        # then call path rm to delete the folders
        # then delete the whole folder
