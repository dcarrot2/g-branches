"""UI components using Rich and InquirerPy."""

from InquirerPy import inquirer
from rich.columns import Columns
from rich.console import Console, Group
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Column, Table
from rich.text import Text

from .models import BranchInfo


class BranchUI:
    """Handles user interface for branch operations."""

    def __init__(self) -> None:
        """Initialize the BranchUI with a Rich console."""
        # Force terminal and enable color support
        self.console = Console(
            force_terminal=True,
            color_system="auto",  # Auto-detect best color support
            legacy_windows=False,
        )
        # Maintain reference of currently listed panels
        self.panels = []

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

    def display_branch_details(self, branch: BranchInfo, diffs: list[str]) -> None:
        """
        Show detailed branch information with syntax-highlighted diffs side by side.

        Args:
            branch: BranchInfo object with branch details
            diffs: List of diff outputs to display (one per commit)
        """
        # Prepare branch information panel
        info_text = f"""[bold cyan]Branch:[/bold cyan] {branch.name}
[bold cyan]Commit:[/bold cyan] {branch.commit_hash}
[bold cyan]Date:[/bold cyan] {branch.formatted_date}
[bold cyan]Message:[/bold cyan] {branch.commit_message}
[bold cyan]Type:[/bold cyan] {"Remote" if branch.is_remote else "Local"}
"""
        branch_panel = Panel(info_text, title="Branch Details", border_style="blue")

        # Prepare diff content
        diff_content_parts = []
        if diffs:
            total_diffs = len(diffs)
            for idx, diff in enumerate(diffs, start=1):
                if diff and diff.strip() and diff != "No changes in this commit":
                    # Create panel title
                    if total_diffs > 1:
                        panel_title = f"Commit Diff {idx} of {total_diffs}"
                    else:
                        panel_title = "Commit Diff"

                    # Manually colorize diff for reliable highlighting
                    colored_diff = Text()
                    for line in diff.split("\n"):
                        if line.startswith("+++"):
                            colored_diff.append(line + "\n", style="cyan")
                        elif line.startswith("---"):
                            colored_diff.append(line + "\n", style="magenta")
                        elif line.startswith("@@"):
                            colored_diff.append(line + "\n", style="blue")
                        elif line.startswith("+"):
                            colored_diff.append(line + "\n", style="green")
                        elif line.startswith("-"):
                            colored_diff.append(line + "\n", style="red")
                        elif line.startswith("diff --git"):
                            colored_diff.append(line + "\n", style="yellow")
                        elif line.startswith("index "):
                            colored_diff.append(line + "\n", style="dim")
                        else:
                            colored_diff.append(line + "\n")
                    
                    # Remove trailing newline
                    if colored_diff:
                        colored_diff.rstrip()
                    
                    diff_panel = Panel(
                        colored_diff,
                        title=panel_title,
                        border_style="yellow",
                        padding=(0, 1),
                    )
                    diff_content_parts.append(diff_panel)
                elif idx == 1:
                    # Only show "No changes" message for the first diff if it's empty
                    no_changes_panel = Panel(
                        "[dim]No changes in this commit[/dim]",
                        title="Commit Diff",
                        border_style="dim",
                    )
                    diff_content_parts.append(no_changes_panel)
        else:
            no_changes_panel = Panel(
                "[dim]No changes in this commit[/dim]",
                title="Commit Diff",
                border_style="dim",
            )
            diff_content_parts.append(no_changes_panel)

        # Combine branch info and diffs in columns
        # Use pager for scrollable content with colors preserved
        # Create a renderable group for the diff content
        diff_group = Group(*diff_content_parts) if diff_content_parts else Group()
        
        # Display side by side using Columns
        columns = Columns(
            [branch_panel, diff_group],
            equal=False,
            expand=True,
        )
        
        # Use pager with styles enabled to preserve colors
        with self.console.pager(styles=True):
            self.console.print(columns)

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
