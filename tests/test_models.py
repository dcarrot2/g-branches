"""Tests for data models."""

from datetime import datetime

from g_branches.models import BranchInfo


def test_branch_info_display_name_current() -> None:
    """Test display_name for current branch."""
    branch = BranchInfo(
        name="main",
        commit_hash="abc123",
        commit_date=datetime.now(),
        commit_message="Test",
        is_current=True,
        is_remote=False,
    )
    assert branch.display_name == "* main"


def test_branch_info_display_name_not_current() -> None:
    """Test display_name for non-current branch."""
    branch = BranchInfo(
        name="feature",
        commit_hash="abc123",
        commit_date=datetime.now(),
        commit_message="Test",
        is_current=False,
        is_remote=False,
    )
    assert branch.display_name == "  feature"


def test_branch_info_short_hash() -> None:
    """Test short_hash property."""
    branch = BranchInfo(
        name="main",
        commit_hash="abc123def456ghi789",
        commit_date=datetime.now(),
        commit_message="Test",
        is_current=False,
        is_remote=False,
    )
    assert branch.short_hash == "abc123d"
    assert len(branch.short_hash) == 7


def test_branch_info_formatted_date() -> None:
    """Test formatted_date property."""
    test_date = datetime(2024, 1, 15, 10, 30, 45)
    branch = BranchInfo(
        name="main",
        commit_hash="abc123",
        commit_date=test_date,
        commit_message="Test",
        is_current=False,
        is_remote=False,
    )
    assert branch.formatted_date == "2024-01-15 10:30:45"
