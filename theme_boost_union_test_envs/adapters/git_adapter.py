import os
from os import PathLike

from git import Repo
from git.exc import GitCommandError
from loguru import logger


class GitAdapter:
    def __init__(self, repo_url: str, working_dir: str) -> None:
        self.repo_url = repo_url
        self.working_dir = working_dir

    def clone_repo(self, name: str) -> str | PathLike[str] | None:
        logger.info("cloning repository...")
        repo_dir = f"{self.working_dir}/{name}/theme"
        if not os.path.exists(repo_dir):
            repo = Repo.clone_from(self.repo_url, repo_dir)
            logger.info("done cloning")
            return repo.working_tree_dir
        else:
            raise ValueError("Repo already exists")
