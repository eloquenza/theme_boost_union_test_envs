import bisect
import shutil
from pathlib import Path

from ..adapters import GitAdapter
from ..cross_cutting import config, log
from ..domain import MoodleCache
from ..domain.git import GitReference
from ..exceptions import VersionArgumentNeededError


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
        log().info(f"initializing new test infrastructure named '{name}'")
        self.git.clone_repo(name, git_ref)
        log().info("done init - find your test infrastructure here:")
        log().info(f"\tpath: {config().working_dir / name}")

    def build(self, *versions: str) -> None:
        if not versions:
            raise VersionArgumentNeededError
        infra_path = config().working_dir
        # check the existing infrastructure if the selected moodle versions are already present
        new_versions = self._check_existing_infrastructure(infra_path, *versions)
        if not new_versions:
            log().info(
                "not building new envs - test envs already presented for selected moodle versions"
            )
            return
        # create a new test environment for the remaining moodle versions
        log().info("building envs for the following versions:")
        for ver in new_versions:
            log().info(f"* {ver}")
        # TODO: mkdir moodles; don't throw error if it already exists
        for ver in new_versions:
            log().info(f"{20*'-'} {ver} {20*'-'}")
            log().info("creating test env")
            vers_path = infra_path / ver
            vers_path.mkdir(exist_ok=True)
            # unpacking the archive will created a folder called "moodle-{ver}"
            # rename the folder afterwards to ensure moodle sources are at the
            # same location in every created test infrastructure
            shutil.unpack_archive(self.moodle_cache.get(ver), vers_path)
            shutil.move(vers_path / f"moodle-{ver}", vers_path / "moodle")
            # TODO: pull moodle-docker into it
            # TODO: replace all the params from moodle-docker with the correct ones:
            # TODO: * adjust the mounts in the docker-compose:
            # TODO:     * add theme mount
            # TODO:     * add moodle sources mount
            # TODO: * COMPOSE_NAME: given by init / folder_name
            # TODO: * MOODLE_WWW_PORT: 0.0.0.0:$empty_port
            # TODO: * NGINX_SERVER_NAME: see COMPOSE_NAME
            # TODO: * absolute path for Moodle source
            # TODO: * absolute path for "Boost Union" theme
            # TODO: * MOODLE_VER
            # TODO: * MOODLE_DOCKER_PHP_VERSION
            log().info(f"test env for {ver} done")
            # moodles are cooked al-dente; enjoy

    def _check_existing_infrastructure(self, path: Path, *versions: str) -> list[str]:
        # return list of moodle versions without a existing test environment
        new_versions: list[str] = []
        for ver in versions:
            vers_path = path / ver
            if not vers_path.exists():
                bisect.insort(new_versions, ver)
        return new_versions

    def teardown(self, name: str) -> None:
        log().info(f"teardown test bed of {name}")
        # TODO: then remove file from nginx; to make sure the moodles cannot be served anymore
        # TODO: then call path rm to delete the folders
        # TODO: then delete the whole folder
