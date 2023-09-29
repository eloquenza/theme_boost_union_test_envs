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

    def build(self, infrastructure: Path, *versions: str) -> None:
        if not versions:
            raise VersionArgumentNeededError()
        moodles = infrastructure / "moodles"
        if not moodles.exists():
            moodles.mkdir()
            new_versions = [*versions]
        else:
            # check the existing infrastructure if the selected moodle versions are already present
            new_versions = self._check_existing_infrastructure(moodles, *versions)
            if not new_versions:
                log().info(
                    "not building new envs - test envs already presented for selected moodle versions"
                )
                return
        # create a new test environment for the remaining moodle versions
        log().info("building envs for the following versions:")
        for ver in new_versions:
            log().info(f"* {ver}")
        for ver in new_versions:
            moodle_archive_path = self.moodle_cache.get(ver)
            log().info(f"{20*'-'} {ver} {20*'-'}")
            log().info("creating test env")
            version_path = moodles / ver
            moodle_source_path = version_path / "moodle"
            version_path.mkdir(exist_ok=True)
            # unpacking the archive will created a folder called "moodle-{ver}"
            # rename the folder afterwards to ensure moodle sources are at the
            # same location in every created test infrastructure
            shutil.unpack_archive(moodle_archive_path, version_path)
            extracted_path = version_path / f"moodle-{ver}"
            shutil.move(extracted_path, moodle_source_path)
            log().info(f"extracted moodle {ver} to {moodle_source_path}")
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
        log().info("your moodles are cooked al-dente; enjoy")

    def _check_existing_infrastructure(self, path: Path, *versions: str) -> list[str]:
        # return list of moodle versions without a existing test environment
        new_versions: list[str] = []
        for ver in versions:
            vers_path = path / ver
            if not vers_path.exists():
                bisect.insort(new_versions, ver)
        return new_versions

    def teardown(self, infrastructure_name: str) -> None:
        log().info(f"teardown test bed of {infrastructure_name}")
        # TODO: then remove file from nginx; to make sure the moodles cannot be served anymore
        # TODO: then call path rm to delete the folders
        # TODO: then delete the whole folder
