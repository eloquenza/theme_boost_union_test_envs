import os
from os import PathLike

from git import Repo
from loguru import logger

from ..utils.dataclasses import GitReference, GitReferenceType


class GitAdapter:
    def __init__(self, repo_url: str, working_dir: str) -> None:
        self.repo_url = repo_url
        self.working_dir = working_dir

    def clone_repo(
        self, name: str, git_ref: GitReference
    ) -> str | PathLike[str] | None:
        logger.info("cloning repository...")
        repo_dir = f"{self.working_dir}/{name}/theme"
        if not os.path.exists(repo_dir):
            if git_ref.type == GitReferenceType.BRANCH:
                repo = Repo.clone_from(self.repo_url, repo_dir, branch=git_ref.ref)
            elif git_ref.type == GitReferenceType.COMMIT:
                repo = Repo.clone_from(self.repo_url, repo_dir)
                repo.git.checkout(git_ref.ref)
            elif git_ref.type == GitReferenceType.PULL_REQUEST:
                repo = Repo.clone_from(self.repo_url, repo_dir)
                origin = repo.remote("origin")
                # fetch all PRs from GitHub
                origin.fetch(
                    refspec="+refs/pull/*/head:refs/remotes/origin/pr/*",
                )
                branch_name = f"pr/{git_ref.ref}"
                repo.create_head(
                    branch_name, origin.refs[branch_name]
                ).set_tracking_branch(origin.refs[branch_name]).checkout()
            else:
                # checkout main branch as this is the only sensible default
                repo = Repo.clone_from(self.repo_url, repo_dir)
            # checked out reference is pushed into another var to avoid handling a TypeError in case we wanna check out a commit directly because GitPython complains about the HEAD being in a detached state then.
            logger.info(f"done cloning, checked out: {git_ref}")
            return repo.working_tree_dir
        else:
            raise ValueError("Repo already exists")
