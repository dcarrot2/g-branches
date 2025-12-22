"""Tests for CLI interface."""

from pathlib import Path

import pytest
from git import Repo
from typer.testing import CliRunner

from g_branches.cli import app

runner = CliRunner()


def test_cli_with_invalid_repo(tmp_path: Path) -> None:
    """Test CLI with invalid repository path."""
    result = runner.invoke(app, ["--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "Not a git repository" in result.stdout


def test_cli_help() -> None:
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "List git branches sorted by latest commit" in result.stdout
