import shutil
from pathlib import Path

from loguru import logger

from ..adapters import GitAdapter
from ..domain import MoodleCache
from ..utils.config import get_config
from ..utils.dataclasses import GitReference


class TestInfrastructureService:
    def __init__(
        self,
        git: GitAdapter,
        moodle_cache: MoodleCache,
    ) -> None:
        self.git = git
        self.moodle_cache = moodle_cache

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

    def build(self, *versions: str) -> None:
        if not versions:
            raise ValueError
        logger.info("build envs for the following versions:")
        # mkdir moodles; don't throw error if it already exists
        infra_path = get_config().working_dir
        logger.info("creating infra path")
        infra_path.mkdir(exist_ok=True)
        for ver in versions:
            # check if ver already exists; continue then
            vers_path = infra_path / ver
            if vers_path.exists():
                logger.info(f"test env for {ver} already exists")
                continue
            logger.info(f"{ver} moodle test env does not exist yet")
            logger.info("creating test env")
            vers_path.mkdir(exist_ok=True)
            # unpacking the archive will created a folder called "moodle-{ver}"
            # rename the folder afterwards to ensure moodle sources are at the
            # same location in every created test infrastructure
            shutil.unpack_archive(self.moodle_cache.get(ver), vers_path)
            shutil.move(vers_path / f"moodle-{ver}", vers_path / "moodle")
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
