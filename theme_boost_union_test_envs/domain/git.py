from dataclasses import dataclass
from enum import Enum

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
