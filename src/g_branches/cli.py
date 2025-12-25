"""Command-line interface for g_branches."""

from pathlib import Path

import typer

from .exceptions import GitOperationError, GitRepositoryError, NoBranchesFoundError
from .git_operations import GitBranchManager
from .ui import BranchUI

app = typer.Typer(
    name="g-branches",
    help="Interactive git branch explorer and switcher",
    add_completion=False,
)


@app.command()
def main(
    remote: bool = typer.Option(
        False,
        "--remote",
        "-r",
        help="Include remote branches in the list",
    ),
    auto_switch: bool = typer.Option(
        False,
        "--switch",
        "-s",
        help="Automatically switch to selected branch without confirmation",
    ),
    repo_path: Path | None = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to git repository (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
) -> None:
    """
    List git branches sorted by latest commit and interactively explore them.

    Shows branches in a table format sorted by commit date (newest first).
    Select a branch to view its last commit details and optionally switch to it.
    """
    ui = BranchUI()

    try:
        # Initialize git manager
        git_manager = GitBranchManager(repo_path)

        # Fetch branches
        branches = git_manager.get_all_branches(include_remote=remote)

        # Display branches table
        ui.display_branches_table(branches)

        # Interactive branch selection
        selected_branch = ui.select_branch(branches)

        if selected_branch is None:
            # User cancelled selection
            raise typer.Exit(0)

        # Get and display branch details
        try:
            diffs = git_manager.get_branch_diff(selected_branch.name)
        except GitOperationError as e:
            ui.display_error(f"Could not get diff: {e}")
            diffs = []

        ui.display_branch_details(selected_branch, diffs)

        # Don't allow switching to current branch
        if selected_branch.is_current:
            ui.console.print("[yellow]You are already on this branch.[/yellow]")
            raise typer.Exit(0)

        # Show checkout command
        ui.show_checkout_command(selected_branch.name)

        # Confirm and execute checkout
        should_checkout = auto_switch or ui.confirm_checkout(selected_branch.name)

        if should_checkout:
            try:
                git_manager.checkout_branch(selected_branch.name)
                ui.display_success(
                    f"Successfully switched to branch: {selected_branch.name}"
                )
            except GitOperationError as e:
                ui.display_error(f"Failed to switch branch: {e}")
                raise typer.Exit(1) from e
        else:
            ui.console.print("[dim]Branch switch cancelled.[/dim]")

    except GitRepositoryError as e:
        ui.display_error(str(e))
        ui.console.print(
            "[yellow]Make sure you're in a git repository or provide "
            "a valid path with --path[/yellow]"
        )
        raise typer.Exit(1) from e

    except NoBranchesFoundError as e:
        ui.display_error(str(e))
        raise typer.Exit(1) from e

    except GitOperationError as e:
        ui.display_error(f"Git operation failed: {e}")
        raise typer.Exit(1) from e

    except KeyboardInterrupt:
        ui.console.print("\n[yellow]Cancelled by user.[/yellow]")
        raise typer.Exit(0) from None

    except Exception as e:
        ui.display_error(f"Unexpected error: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
