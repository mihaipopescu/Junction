from pathlib import Path
from enum import Enum
from git import Repo, Commit, NULL_TREE, Diff


def find_repository_root(path: Path):
    path = path.resolve()

    def _find_repository_root(path: Path):
        if path.joinpath("./.git").exists():
            return path
        elif path.parent == path:
            # when at a root, the parent will be the same as path, so we bottomed out; no repository found
            return None
        else:
            return _find_repository_root(path.parent)

    return _find_repository_root(path)


def find_commits_on_branch_after(branch_name: str, start_commit_sha: str, repo: Repo):
    reverse_chronological_commits = list(
        repo.iter_commits(f"{start_commit_sha}..{branch_name}", first_parent=True)
    )
    reverse_chronological_commits.reverse()
    return reverse_chronological_commits


class ModificationType(Enum):
    ADD = 1
    RENAME = 2
    DELETE = 3
    MODIFY = 4
    UNKNOWN = 5


class Modification:
    def __init__(self, old_path: str, new_path: str, change_type: ModificationType):
        self._old_path = Path(old_path) if old_path is not None else None
        self._new_path = Path(new_path) if new_path is not None else None
        self.change_type = change_type

    @property
    def previous_path(self):
        return self._old_path if self.change_type == ModificationType.RENAME else None

    @property
    def path(self):
        return self._new_path if self._new_path else self._old_path

    @staticmethod
    def _determine_modification_type(diff: Diff):
        if diff.new_file:
            return ModificationType.ADD
        if diff.deleted_file:
            return ModificationType.DELETE
        if diff.renamed_file:
            return ModificationType.RENAME
        if diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
            return ModificationType.MODIFY

        return ModificationType.UNKNOWN

    @staticmethod
    def from_diff(diff: Diff):
        old_path = diff.a_path
        new_path = diff.b_path
        change_type = Modification._determine_modification_type(diff)

        return Modification(old_path, new_path, change_type)

    def __repr__(self):
        return f"{self.change_type} {self.path}"


def get_modifications(commit: Commit):
    if commit.parents:
        diffs = commit.parents[0].diff(commit)
    else:
        # initial commit
        diffs = commit.diff(NULL_TREE)

    return [Modification.from_diff(d) for d in diffs]