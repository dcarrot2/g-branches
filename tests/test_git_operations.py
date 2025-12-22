"""Tests for git operations."""

from pathlib import Path

import pytest
from git import Repo

from g_branches.exceptions import GitRepositoryError, NoBranchesFoundError
from g_branches.git_operations import GitBranchManager


def test_git_manager_init_with_valid_repo(tmp_git_repo: Repo) -> None:
    """Test GitBranchManager initialization with valid repository."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))
    assert manager.repo is not None


def test_git_manager_init_with_invalid_repo(tmp_path: Path) -> None:
    """Test GitBranchManager initialization with invalid repository."""
    with pytest.raises(GitRepositoryError):
        GitBranchManager(tmp_path)


def test_get_current_branch(tmp_git_repo: Repo) -> None:
    """Test getting current branch name."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))
    current = manager.get_current_branch()
    assert current == "main"


def test_get_all_branches(tmp_git_repo: Repo) -> None:
    """Test fetching all branches."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))
    branches = manager.get_all_branches(include_remote=False)

    assert len(branches) == 3
    branch_names = [b.name for b in branches]
    assert "main" in branch_names
    assert "feature/test" in branch_names
    assert "bugfix/test" in branch_names

    # Verify sorted by date (newest first)
    for i in range(len(branches) - 1):
        assert branches[i].commit_date >= branches[i + 1].commit_date


def test_get_all_branches_marks_current(tmp_git_repo: Repo) -> None:
    """Test that current branch is marked correctly."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))
    branches = manager.get_all_branches(include_remote=False)

    current_branches = [b for b in branches if b.is_current]
    assert len(current_branches) == 1
    assert current_branches[0].name == "main"


def test_get_branch_diff(tmp_git_repo: Repo) -> None:
    """Test getting branch diff."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))
    diff = manager.get_branch_diff("feature/test")

    assert diff is not None
    assert isinstance(diff, str)


def test_checkout_branch(tmp_git_repo: Repo) -> None:
    """Test checking out a branch."""
    manager = GitBranchManager(Path(tmp_git_repo.working_dir))

    # Checkout feature branch
    manager.checkout_branch("feature/test")
    current = manager.get_current_branch()
    assert current == "feature/test"

    # Checkout back to main
    manager.checkout_branch("main")
    current = manager.get_current_branch()
    assert current == "main"
