import shutil
from pathlib import Path
from typing import Any

from ..cross_cutting import config, log, template_engine
from ..domain import MoodleCache, TestContainer
from ..domain.git import GitReference, GitRepository
from ..exceptions import VersionArgumentNeededError


class TestInfrastructure:
    def __init__(
        self,
        directory: Path,
        boost_union_repo: GitRepository,
        moodle_cache: MoodleCache,
    ) -> None:
        self.directory = directory
        self.boost_union_repo = boost_union_repo
        self.moodle_cache = moodle_cache
        self.template_engine = template_engine()

    def setup(
        self,
        git_ref: GitReference,
    ) -> None:
        log().info(f"initializing new test infrastructure named '{self.directory}'")
        self.boost_union_repo.clone_repo(self.directory, git_ref)
        moodles = self._get_moodles_dir()
        if not moodles.exists():
            log().info("oh, no moodles yet. starting the stove...")
            moodles.mkdir()
        log().info("done init - find your test infrastructure here:")
        log().info(f"\tpath: {self.directory }")

    def build(self, *versions: str) -> dict[Any, Any]:
        if not versions:
            raise VersionArgumentNeededError()
        moodles = self._get_moodles_dir()
        # check the existing infrastructure if the selected moodle versions are already present
        new_versions = self._find_sources_for_versions(moodles, *versions)
        if not new_versions:
            log().info(
                "not building new envs - test envs already presented for selected moodle versions"
            )
            return {}
        # create a new test environment for the remaining moodle versions
        log().info("building envs for the following versions:")
        for version in new_versions:
            log().info(f"* {version}")
        docker_sources = config().moodle_docker_dir
        built_moodles = {}
        for version_nr, archive_path in new_versions.items():
            log().info(f"{20*'-'} {version_nr} {20*'-'}")
            log().info("creating test env")
            moodle_version_path = moodles / version_nr
            moodle_source_path = moodle_version_path / "moodle"
            moodle_version_path.mkdir(exist_ok=True)
            # unpacking the archive will created a folder called "moodle-{ver}"
            # rename the folder afterwards to ensure moodle sources are at the
            # same location in every created test infrastructure
            shutil.unpack_archive(archive_path, moodle_version_path)
            extracted_path = moodle_version_path / f"moodle-{version_nr}"
            shutil.move(extracted_path, moodle_source_path)
            log().info(f"extracted moodle {version} to {moodle_source_path}")
            # dirs_exist_ok needed so function doesn't raise FileExistsError
            shutil.copytree(docker_sources, moodle_version_path, dirs_exist_ok=True)
            log().info(f"copied docker files to {moodle_version_path}")
            log().info(
                "create environment file with needed vars for our docker containers"
            )
            shutil.copy(
                moodle_version_path / "config.docker-template.php",
                moodle_source_path / "config.php",
            )
            self.template_engine.docker_customisation(
                moodle_version_path, self.directory / "theme" / "boost_union"
            )
            self.template_engine.environment_file(
                moodle_version_path, self.directory.name, version_nr
            )
            container = TestContainer(moodle_version_path)
            container.create()
            host, port, pw = container.container_access_info()
            built_moodles[version_nr] = {
                "status": "CREATED",
                "url": f"https://{host}"
                if config().is_proxied
                else f"http://{host}:{port}",
                "admin_pw": pw,
            }
            self.template_engine.nginx_config(self.directory.name, version_nr, port)
            # TODO: replace all the params from moodle-docker with the correct ones:
            # TODO: * NGINX_SERVER_NAME: see COMPOSE_NAME
            # TODO: * MOODLE_VER
            # TODO: * MOODLE_DOCKER_PHP_VERSION
            log().info(f"test env for {version_nr} done")
        log().info("your moodles are cooked al-dente; enjoy")
        return built_moodles

    def _find_sources_for_versions(self, path: Path, *versions: str) -> dict[str, Path]:
        # return dict of moodles (versions + their source archives) without a existing test environment
        sources_to_versions: dict[str, Path] = {}
        for ver in versions:
            vers_path = path / ver
            if not vers_path.exists():
                sources_to_versions |= {ver: self.moodle_cache.get(ver)}
        return sources_to_versions

    def _get_moodles_dir(self) -> Path:
        return self.directory / "moodles"

    def teardown(self, infrastructure_name: str) -> None:
        log().info(f"starting teardown of test infrastructure {infrastructure_name}")
        # TODO: then remove file from nginx; to make sure the moodles cannot be served anymore
        # TODO: then call path rm to delete the folders
        # TODO: then delete the whole folder
        # pathlib functions require the dir to be empty, but we just can safely
        # delete all files now, so we resort to shutil
        if self.directory.exists():
            shutil.rmtree(self.directory)
            log().info(f"removed test infrastructure {self.directory.name}")
