"""UI components using Rich and InquirerPy."""

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .models import BranchInfo


class BranchUI:
    """Handles user interface for branch operations."""

    def __init__(self) -> None:
        """Initialize the BranchUI with a Rich console."""
        self.console = Console()

    def display_branches_table(self, branches: list[BranchInfo]) -> None:
        """
        Display branches in a formatted table.

        Args:
            branches: List of BranchInfo objects to display
        """
        table = Table(title="Git Branches (sorted by latest commit)", show_header=True)

        table.add_column("Branch", style="cyan", no_wrap=True)
        table.add_column("Commit", style="magenta")
        table.add_column("Date", style="yellow")
        table.add_column("Message", style="white")

        for branch in branches:
            # Highlight current branch
            branch_style = "bold green" if branch.is_current else "cyan"
            branch_name = branch.name
            if branch.is_current:
                branch_name = f"* {branch_name}"

            table.add_row(
                f"[{branch_style}]{branch_name}[/{branch_style}]",
                branch.short_hash,
                branch.formatted_date,
                branch.commit_message[:60] + "..."
                if len(branch.commit_message) > 60
                else branch.commit_message,
            )

        self.console.print(table)
        self.console.print()

    def select_branch(self, branches: list[BranchInfo]) -> BranchInfo | None:
        """
        Interactive branch selection using InquirerPy.

        Args:
            branches: List of BranchInfo objects to choose from

        Returns:
            Selected BranchInfo or None if cancelled
        """
        choices = [
            {
                "name": (
                    f"{'* ' if b.is_current else '  '}{b.name} "
                    f"({b.short_hash}) - {b.commit_message[:50]}"
                ),
                "value": b,
            }
            for b in branches
        ]

        result = inquirer.select(  # type: ignore[attr-defined]
            message="Select a branch to view details:",
            choices=choices,
            default=None,
            qmark="?",
            amark="✓",
        ).execute()

        return result  # type: ignore[no-any-return]

    def display_branch_details(self, branch: BranchInfo, diff: str) -> None:
        """
        Show detailed branch information with syntax-highlighted diff.

        Args:
            branch: BranchInfo object with branch details
            diff: Diff output to display
        """
        # Display branch information
        info_text = f"""[bold cyan]Branch:[/bold cyan] {branch.name}
[bold cyan]Commit:[/bold cyan] {branch.commit_hash}
[bold cyan]Date:[/bold cyan] {branch.formatted_date}
[bold cyan]Message:[/bold cyan] {branch.commit_message}
[bold cyan]Type:[/bold cyan] {"Remote" if branch.is_remote else "Local"}
"""
        panel = Panel(info_text, title="Branch Details", border_style="blue")
        self.console.print(panel)
        self.console.print()

        # Display diff with syntax highlighting
        if diff and diff != "No changes in this commit":
            self.console.print("[bold yellow]Last Commit Diff:[/bold yellow]")
            # Limit diff length for readability
            max_lines = 100
            diff_lines = diff.split("\n")
            if len(diff_lines) > max_lines:
                diff = "\n".join(diff_lines[:max_lines])
                diff += f"\n\n... (truncated, {len(diff_lines) - max_lines} more lines)"

            syntax = Syntax(diff, "diff", theme="monokai", line_numbers=False)
            self.console.print(syntax)
        else:
            self.console.print("[dim]No changes in this commit[/dim]")

        self.console.print()

    def show_checkout_command(self, branch_name: str) -> None:
        """
        Display the git checkout command.

        Args:
            branch_name: Name of the branch
        """
        command = f"git checkout {branch_name}"
        if branch_name.startswith("origin/"):
            local_name = branch_name.replace("origin/", "")
            command = f"git checkout -b {local_name} {branch_name}"

        self.console.print(
            f"[bold green]To switch to this branch, run:[/bold green] {command}"
        )
        self.console.print()

    def confirm_checkout(self, branch_name: str) -> bool:
        """
        Ask user to confirm branch checkout.

        Args:
            branch_name: Name of the branch to checkout

        Returns:
            True if user confirms, False otherwise
        """
        result: bool = inquirer.confirm(  # type: ignore[attr-defined]
            message=f"Do you want to switch to '{branch_name}' now?",
            default=False,
            qmark="?",
            amark="✓",
        ).execute()

        return result

    def display_error(self, message: str) -> None:
        """
        Display an error message in a red panel.

        Args:
            message: Error message to display
        """
        panel = Panel(
            f"[bold red]{message}[/bold red]",
            title="Error",
            border_style="red",
        )
        self.console.print(panel)

    def display_success(self, message: str) -> None:
        """
        Display a success message in a green panel.

        Args:
            message: Success message to display
        """
        panel = Panel(
            f"[bold green]{message}[/bold green]",
            title="Success",
            border_style="green",
        )
        self.console.print(panel)
