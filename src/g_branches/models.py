"""Data models for git branch information."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BranchInfo:
    """Information about a git branch."""

    name: str
    commit_hash: str
    commit_date: datetime
    commit_message: str
    is_current: bool
    is_remote: bool

    @property
    def display_name(self) -> str:
        """Format branch name with current indicator."""
        prefix = "* " if self.is_current else "  "
        return f"{prefix}{self.name}"

    @property
    def short_hash(self) -> str:
        """Return short commit hash (7 characters)."""
        return self.commit_hash[:7]

    @property
    def formatted_date(self) -> str:
        """Return human-readable commit date."""
        return self.commit_date.strftime("%Y-%m-%d %H:%M:%S")
