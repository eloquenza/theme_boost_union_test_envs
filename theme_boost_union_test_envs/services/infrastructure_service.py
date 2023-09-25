from loguru import logger

from ..adapters import GitAdapter
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
            repo_path = self.git.clone_repo(name, git_ref)
            logger.info("done init - find your test infrastructure here:")
            logger.info(f"\tpath: {repo_path}")
        except ValueError as e:
            logger.error(f"{e}")
            raise e

    def build(self, *versions: list[str]) -> None:
        if not versions:
            raise ValueError
        logger.info("build envs for the following versions:")
        for ver in versions:
            logger.info(f"* {ver}")

    def teardown(self, name: str) -> None:
        logger.info(f"teardown test bed of {name}")
