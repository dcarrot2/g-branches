"""Pytest fixtures for g_branches tests."""

from datetime import datetime
from pathlib import Path

import pytest
from git import Repo

from g_branches.models import BranchInfo


@pytest.fixture
def sample_branches() -> list[BranchInfo]:
    """Create sample BranchInfo objects for testing."""
    return [
        BranchInfo(
            name="main",
            commit_hash="abc123def456",
            commit_date=datetime(2024, 1, 15, 10, 30, 0),
            commit_message="Initial commit",
            is_current=True,
            is_remote=False,
        ),
        BranchInfo(
            name="feature/new-feature",
            commit_hash="def456ghi789",
            commit_date=datetime(2024, 1, 16, 14, 20, 0),
            commit_message="Add new feature",
            is_current=False,
            is_remote=False,
        ),
        BranchInfo(
            name="bugfix/critical-fix",
            commit_hash="ghi789jkl012",
            commit_date=datetime(2024, 1, 17, 9, 15, 0),
            commit_message="Fix critical bug in production",
            is_current=False,
            is_remote=False,
        ),
    ]


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Repo:
    """Create a temporary git repository with some branches for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize repo
    repo = Repo.init(repo_path)

    # Configure git
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")

    # Create initial commit on main
    test_file = repo_path / "README.md"
    test_file.write_text("# Test Repository\n")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Create feature branch
    feature_branch = repo.create_head("feature/test")
    feature_branch.checkout()
    test_file.write_text("# Test Repository\n\nFeature content\n")
    repo.index.add(["README.md"])
    repo.index.commit("Add feature")

    # Create another branch
    bugfix_branch = repo.create_head("bugfix/test")
    bugfix_branch.checkout()
    test_file.write_text("# Test Repository\n\nFeature content\nBugfix\n")
    repo.index.add(["README.md"])
    repo.index.commit("Fix bug")

    # Return to main
    repo.heads.main.checkout()

    return repo
