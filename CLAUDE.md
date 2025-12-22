# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`g-branches` is a Python CLI tool for interactively viewing and switching between git branches. It provides a beautiful terminal interface with branch sorting by commit date, detailed commit viewing, and safe branch switching.

## Commands

### Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running the CLI

```bash
# Run as module
python -m g_branches

# Or use installed commands (after pip install -e .)
g-branches
gb  # Short alias
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=g_branches --cov-report=html

# Run specific test file
pytest tests/test_git_operations.py

# Run with verbose output
pytest -v
```

### Linting & Formatting

```bash
# Check code with ruff
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/

# Type check with mypy
mypy src/g_branches

# Run all quality checks
ruff check . --fix && ruff format . && mypy src/g_branches && pytest
```

## Architecture

### Module Organization (src/g_branches/)

The project follows clean architecture with clear separation of concerns:

1. **models.py** - Data layer
   - `BranchInfo` dataclass: Represents git branch metadata
   - Properties: `display_name`, `short_hash`, `formatted_date`

2. **exceptions.py** - Error handling
   - `GitRepositoryError`: Not in a git repository
   - `GitOperationError`: Git command failures
   - `NoBranchesFoundError`: Empty repository

3. **git_operations.py** - Git integration layer
   - `GitBranchManager` class: Wraps GitPython for type-safe operations
   - Key methods:
     - `get_all_branches()`: Fetches and sorts branches by commit date
     - `get_branch_diff()`: Retrieves last commit diff
     - `checkout_branch()`: Switches branches (handles remote tracking)
     - `get_current_branch()`: Returns active branch name
   - Handles bytes/str conversion for commit messages and diffs
   - Implements parent directory search for git repositories

4. **ui.py** - User interface layer
   - `BranchUI` class: Rich + InquirerPy integration
   - `display_branches_table()`: Rich table with color-coded current branch
   - `select_branch()`: Interactive selection with fuzzy search
   - `display_branch_details()`: Syntax-highlighted diff output
   - `confirm_checkout()`: Yes/no prompt for safety
   - Error/success message helpers

5. **cli.py** - Application entry point
   - Typer application with command-line options
   - Options: `--remote/-r`, `--switch/-s`, `--path/-p`
   - Orchestrates workflow: fetch → display → select → view → switch
   - Comprehensive error handling with user-friendly messages
   - All raised exceptions use `raise ... from e` pattern (B904)

### Key Design Patterns

- **Separation of Concerns**: Git logic, UI, and CLI are completely decoupled
- **Type Safety**: Full type hints with mypy strict mode
- **Error Handling**: Custom exceptions with proper chaining
- **Data Flow**: Models → Git Operations → UI → CLI
- **Encoding Safety**: All git data (messages, diffs) checked for bytes/str

### Dependencies

- **GitPython**: Git repository interaction
- **Rich**: Terminal formatting and tables
- **InquirerPy**: Interactive prompts with fuzzy search
- **Typer**: CLI framework with type hints

## Configuration Notes

### pyproject.toml

- **Build System**: Uses hatchling with src/ layout
- **Entry Points**: `g-branches` and `gb` commands
- **Ruff Config**:
  - Line length: 88
  - Ignores B008 (required for Typer's function call defaults)
  - Enabled rules: E, F, I, N, W, UP, B, C4, SIM
- **Mypy Config**:
  - Strict mode enabled
  - Ignores missing imports for: `git.*`, `InquirerPy.*`

### Type Checking Workarounds

- InquirerPy functions need `# type: ignore[attr-defined]` (lines ui.py:73, 146)
- Git commit messages/diffs require bytes/str checks due to GitPython API

## Testing Strategy

- **conftest.py**: Provides `tmp_git_repo` fixture with pre-created branches
- **test_models.py**: Data class properties and formatting
- **test_git_operations.py**: Git integration (requires actual git operations)
- **test_cli.py**: CLI interface using Typer's CliRunner
- All tests use type hints and proper assertions

## Common Development Tasks

### Adding a New CLI Option

1. Add parameter to `cli.py:main()` using `typer.Option()`
2. Update docstring
3. Pass to appropriate handler (GitBranchManager or BranchUI)
4. Add test in `test_cli.py`

### Adding New Git Operations

1. Add method to `GitBranchManager` in `git_operations.py`
2. Handle bytes/str conversion for any git output
3. Wrap in try/except with `GitOperationError`
4. Add test using `tmp_git_repo` fixture
5. Update UI method if display is needed

### Modifying Display

1. Update `BranchUI` methods in `ui.py`
2. Use Rich components (Table, Panel, Syntax, Console)
3. Test manually with `python -m g_branches`

## Important Notes

- Always use `raise ... from e` when re-raising exceptions (B904 compliance)
- Git commit messages and diffs can be bytes or str - always check with isinstance()
- Typer requires function calls in defaults (ignore B008 warning)
- Tests create real git repositories - use `tmp_path` fixture
- Remote branch checkout creates local tracking branches automatically
