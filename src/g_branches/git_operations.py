"""Git operations wrapper using GitPython."""

from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo

from .exceptions import GitOperationError, GitRepositoryError, NoBranchesFoundError
from .models import BranchInfo


class GitBranchManager:
    """Manages git branch operations."""

    def __init__(self, repo_path: Path | None = None) -> None:
        """
        Initialize the GitBranchManager.

        Args:
            repo_path: Path to git repository (default: current directory)

        Raises:
            GitRepositoryError: If the path is not a git repository
        """
        try:
            search_path = str(repo_path) if repo_path else "."
            self.repo = Repo(search_path, search_parent_directories=True)
        except InvalidGitRepositoryError as e:
            raise GitRepositoryError(
                f"Not a git repository: {repo_path or 'current directory'}"
            ) from e

    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.

        Returns:
            Name of the current branch or 'HEAD' if detached

        Raises:
            GitOperationError: If unable to determine current branch
        """
        try:
            # HEAD means that HEAD points directly to a commit instead of a branch.
            if self.repo.head.is_detached:
                return "HEAD (detached)"
            return str(self.repo.active_branch.name)
        except Exception as e:
            raise GitOperationError(f"Failed to get current branch: {e}") from e

    def get_all_branches(self, include_remote: bool = False) -> list[BranchInfo]:
        """
        Fetch all branches sorted by commit date (newest first).

        Args:
            include_remote: Whether to include remote branches

        Returns:
            List of BranchInfo objects sorted by commit date

        Raises:
            NoBranchesFoundError: If no branches are found
            GitOperationError: If unable to fetch branches
        """
        try:
            branches: list[BranchInfo] = []
            current_branch_name = self.get_current_branch()

            # Get local branches
            for branch in self.repo.branches:
                try:
                    commit = branch.commit
                    # Handle commit message as str or bytes
                    message = commit.message
                    if isinstance(message, bytes):
                        message = message.decode("utf-8", errors="replace")
                    commit_msg = message.strip().split("\n")[0]

                    branch_info = BranchInfo(
                        name=branch.name,
                        commit_hash=commit.hexsha,
                        commit_date=commit.committed_datetime,
                        commit_message=commit_msg,
                        is_current=(branch.name == current_branch_name),
                        is_remote=False,
                    )
                    branches.append(branch_info)
                except Exception:
                    # Skip branches that can't be processed
                    continue

            # Get remote branches if requested
            if include_remote:
                for remote in self.repo.remotes:
                    for ref in remote.refs:
                        # Skip HEAD refs
                        if ref.name.endswith("/HEAD"):
                            continue
                        try:
                            commit = ref.commit
                            # Handle commit message as str or bytes
                            message = commit.message
                            if isinstance(message, bytes):
                                message = message.decode("utf-8", errors="replace")
                            commit_msg = message.strip().split("\n")[0]

                            branch_info = BranchInfo(
                                name=ref.name,
                                commit_hash=commit.hexsha,
                                commit_date=commit.committed_datetime,
                                commit_message=commit_msg,
                                is_current=False,
                                is_remote=True,
                            )
                            branches.append(branch_info)
                        except Exception:
                            # Skip remote refs that can't be processed
                            continue

            if not branches:
                raise NoBranchesFoundError("No branches found in repository")

            # Sort by commit date, newest first
            branches.sort(key=lambda b: b.commit_date, reverse=True)
            return branches

        except NoBranchesFoundError:
            raise
        except Exception as e:
            raise GitOperationError(f"Failed to fetch branches: {e}") from e

    def get_branch_diff(self, branch_name: str) -> str:
        """
        Get the diff for the last commit on a branch.

        Args:
            branch_name: Name of the branch

        Returns:
            Diff output as a string

        Raises:
            GitOperationError: If unable to get diff
        """
        try:
            # Handle remote branches
            if "/" in branch_name:
                commit = self.repo.commit(branch_name)
            else:
                branch = self.repo.branches[branch_name]
                commit = branch.commit

            # Get diff for the last commit
            if commit.parents:
                diff = commit.diff(commit.parents[0], create_patch=True)
            else:
                # First commit has no parent
                diff = commit.diff(None, create_patch=True)

            # Format diff output
            diff_text = ""
            for diff_item in diff:
                if diff_item.diff:
                    # Handle diff as str or bytes
                    if isinstance(diff_item.diff, bytes):
                        diff_text += diff_item.diff.decode("utf-8", errors="replace")
                    else:
                        diff_text += diff_item.diff

            return diff_text if diff_text else "No changes in this commit"

        except Exception as e:
            raise GitOperationError(f"Failed to get diff for {branch_name}: {e}") from e

    def checkout_branch(self, branch_name: str) -> None:
        """
        Switch to the specified branch.

        Args:
            branch_name: Name of the branch to checkout

        Raises:
            GitOperationError: If checkout fails
        """
        try:
            # Handle remote branches - create local tracking branch
            if branch_name.startswith("origin/"):
                local_name = branch_name.replace("origin/", "")
                # Check if local branch already exists
                if local_name in [b.name for b in self.repo.branches]:
                    self.repo.git.checkout(local_name)
                else:
                    self.repo.git.checkout("-b", local_name, branch_name)
            else:
                self.repo.git.checkout(branch_name)

        except GitCommandError as e:
            raise GitOperationError(f"Failed to checkout {branch_name}: {e}") from e
        except Exception as e:
            raise GitOperationError(
                f"Unexpected error during checkout of {branch_name}: {e}"
            ) from e
