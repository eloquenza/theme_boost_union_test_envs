from dataclasses import dataclass
from enum import Enum

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
