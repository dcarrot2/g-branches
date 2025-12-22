"""Custom exceptions for g_branches."""


class GitRepositoryError(Exception):
    """Raised when the current directory is not a git repository."""

    pass


class GitOperationError(Exception):
    """Raised when a git operation fails."""

    pass


class NoBranchesFoundError(Exception):
    """Raised when no branches are found in the repository."""

    pass
