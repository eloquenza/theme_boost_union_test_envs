from pathlib import Path

from ..cross_cutting import config, log
from . import GitReference, GitReferenceType, GitRepository


class Testbed:
    def __init__(
        self, moodle_docker_repo: GitRepository, moodle_cache_dir: Path
    ) -> None:
        self.working_dir = config().working_dir
        self.docker_repo = moodle_docker_repo
        self.moodle_cache_dir = moodle_cache_dir

    def init(self) -> None:
        if not self.working_dir.exists():
            log().info(f"creating test bed @ {self.working_dir}")
            self.working_dir.mkdir()
        if not self.moodle_cache_dir.exists():
            log().info(f"creating moodle cache directory @ {self.moodle_cache_dir}")
            self.moodle_cache_dir.mkdir()
        if not (self.working_dir / self.docker_repo.directory).exists():
            log().info(f"cloning moodle_docker repo into {self.working_dir}")
            self.docker_repo.clone_repo(
                self.working_dir, GitReference("master", GitReferenceType.BRANCH)
            )
        else:
            log().info(f"test bed @ {self.working_dir} is already initialized")
