from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from git import Repo

from ..cross_cutting import log

Branch = str
Commit = str
PullRequest = int
Tag = str


class GitReferenceType(str, Enum):
    BRANCH = "branch"
    COMMIT = "commit"
    PULL_REQUEST = "pr"
    TAG = "tag"


@dataclass
class GitReference:
    ref: Branch | Commit | PullRequest | Tag
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
        # Due to the inner workings of GitPython and git itself, we could functionally use checkout for branch, commit or tag, and it would still work.
        # Actually a user could also just use commit and submit a branch name; it would still work.
        # This will allow an infrastructure to be created with the wrong GitReferenceType, but this is largely for information only anyways after the cloning, so it should be fine.
        log().info("cloning repository...")
        # Because a tag is functionally the same as a branch, i.e. identifying a commit by it's hash ID, just (ideally) never changing; we should handle it the same
        if (
            git_ref.type == GitReferenceType.BRANCH
            or git_ref.type == GitReferenceType.TAG
        ):
            # In case we want to check out a branch/tag, let's check it out
            # directly. Saves us a bit of traffic.
            repo = self.__clone_repo(self.directory, branch=git_ref.ref)
        # In any other case, we just want to clone the repo with the default main/master branch
        else:
            repo = self.__clone_repo(self.directory)
        if git_ref.type == GitReferenceType.COMMIT:
            # Because you cannot clone a repo via commit sha directly, we need to check out seperately
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
