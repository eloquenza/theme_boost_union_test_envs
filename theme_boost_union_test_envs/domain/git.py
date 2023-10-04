from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from git import Repo

from ..cross_cutting import log

Branch = str
Commit = str
PullRequest = int


class GitReferenceType(str, Enum):
    BRANCH = "branch"
    COMMIT = "commit"
    PULL_REQUEST = "pr"


@dataclass
class GitReference:
    ref: Branch | Commit | PullRequest
    type: GitReferenceType


class GitRepository:
    def __init__(self, repo_url: str, local_dir: str) -> None:
        self.repo_url = repo_url
        self.directory = Path(local_dir)

    def __clone_repo(self, repo_dir: Path, **clone_args) -> Repo:  # type: ignore
        from ..ui.cli import GitRemoteProgress

        return Repo.clone_from(
            self.repo_url, repo_dir, progress=GitRemoteProgress(), **clone_args  # type: ignore
        )

    def clone_repo(self, destination: Path, git_ref: GitReference) -> None:
        self.directory = destination / self.directory
        log().info("cloning repository...")
        # In case we want to check out a branch, let's check it out directly
        # Saves us a bit of traffic.
        if git_ref.type == GitReferenceType.BRANCH:
            repo = self.__clone_repo(self.directory, branch=git_ref.ref)
        # In any other case, we just want to clone the repo with the default main branch
        else:
            repo = self.__clone_repo(self.directory)
        # Because you cannot clone a repo via commit sha directly, we need to check out seperately
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
            repo.create_head(branch_name, origin.refs[branch_name]).set_tracking_branch(
                origin.refs[branch_name]
            ).checkout()
        log().info(f"done cloning, checked out: {git_ref}")
