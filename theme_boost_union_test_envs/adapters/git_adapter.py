from pathlib import Path

from git import Repo
from loguru import logger

from ..exceptions import NameAlreadyTakenError
from ..utils.config import get_config
from ..utils.dataclasses import GitReference, GitReferenceType


class GitAdapter:
    def __init__(self, repo_url: str) -> None:
        self.repo_url = repo_url
        self.working_dir = get_config().working_dir

    def __clone_repo(self, repo_dir: Path, **clone_args) -> Repo:  # type: ignore
        from ..ui.cli import GitRemoteProgress

        return Repo.clone_from(
            self.repo_url, repo_dir, progress=GitRemoteProgress(), **clone_args  # type: ignore
        )

    def clone_repo(self, name: str, git_ref: GitReference) -> None:
        repo_dir = self.working_dir / name / "theme"
        if repo_dir.exists():
            raise NameAlreadyTakenError("Repo already exists")
        else:
            logger.info("cloning repository...")
            # In case we want to check out a branch, let's check it out directly
            # Saves us a bit of traffic.
            if git_ref.type == GitReferenceType.BRANCH:
                repo = self.__clone_repo(repo_dir, branch=git_ref.ref)
            # In any other case, we just want to clone the repo with the default main branch
            else:
                repo = self.__clone_repo(repo_dir)

            # Because you cannot clone a commit via sha directly, we need to check out seperately
            if git_ref.type == GitReferenceType.COMMIT:
                repo.git.checkout(git_ref.ref)
            # PRs are a bit more tricky as they are not a default Git feature, and GitHub and GitLab handle them a bit differently.
            # Fortunately for us, we only need to handle GitHub for now.
            # TODO: Use defensive programming to guard for GitLab case
            elif git_ref.type == GitReferenceType.PULL_REQUEST:
                origin = repo.remote("origin")
                # fetch all PRs from GitHub
                origin.fetch(
                    refspec="+refs/pull/*/head:refs/remotes/origin/pr/*",
                )
                branch_name = f"pr/{git_ref.ref}"
                repo.create_head(
                    branch_name, origin.refs[branch_name]
                ).set_tracking_branch(origin.refs[branch_name]).checkout()

            # checked out reference is pushed into another var to avoid handling a TypeError in case we wanna check out a commit directly because GitPython complains about the HEAD being in a detached state then.
            logger.info(f"done cloning, checked out: {git_ref}")
