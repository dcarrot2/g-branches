# g-branches

Interactive git branch explorer and switcher CLI tool.

## Features

- View all git branches sorted by latest commit date
- Interactive branch selection with fuzzy search
- View detailed commit information and diffs
- Syntax-highlighted diff output
- Quick branch switching with confirmation
- Support for both local and remote branches
- Beautiful terminal UI with Rich and InquirerPy

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd g_branches

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install -e .
```

## Usage

### Basic Usage

Navigate to a git repository and run:

```bash
g-branches
```

Or use the shorter alias:

```bash
gb
```

### Options

- `--remote`, `-r`: Include remote branches in the list
  ```bash
  g-branches --remote
  ```

- `--switch`, `-s`: Automatically switch to selected branch without confirmation
  ```bash
  g-branches --switch
  ```

- `--path PATH`, `-p PATH`: Specify path to git repository (default: current directory)
  ```bash
  g-branches --path /path/to/repo
  ```

### Examples

```bash
# List all local branches
g-branches

# Include remote branches
g-branches -r

# Explore branches in a different repository
g-branches --path ~/projects/myapp

# Auto-switch mode (no confirmation prompt)
g-branches --switch
```

### Running as a Module

You can also run g-branches as a Python module:

```bash
python -m g_branches
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=g_branches --cov-report=html

# Run specific test file
uv run pytest tests/test_git_operations.py
```

### Code Quality

The project uses `ruff` for linting and formatting, and `mypy` for type checking.

```bash
# Run linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Type checking
uv run mypy src/g_branches
```

### Run All Checks

Before committing, run all checks:

```bash
uv run ruff check . --fix && uv run ruff format . && uv run mypy src/g_branches && uv run pytest
```

## Project Structure

```
g_branches/
├── src/
│   └── g_branches/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Module entry point
│       ├── cli.py               # Typer CLI interface
│       ├── git_operations.py    # Git operations wrapper
│       ├── ui.py                # Rich/InquirerPy UI components
│       ├── models.py            # Data models (BranchInfo)
│       └── exceptions.py        # Custom exceptions
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_models.py
│   ├── test_git_operations.py
│   ├── test_cli.py
│   └── test_ui.py
├── pyproject.toml               # Project configuration
├── .gitignore
└── README.md
```

## Architecture

The project follows a clean architecture with separation of concerns:

- **models.py**: Data classes (BranchInfo) representing git branch information
- **exceptions.py**: Custom exceptions for error handling
- **git_operations.py**: GitBranchManager class wrapping GitPython for all git operations
- **ui.py**: BranchUI class handling all terminal display and user interaction
- **cli.py**: Typer application orchestrating the workflow between git operations and UI

## Requirements

- Python 3.10+
- Git installed on your system
- Terminal with color support for best experience

## Dependencies

- **GitPython**: Git repository interaction
- **Rich**: Beautiful terminal output
- **InquirerPy**: Interactive command-line prompts
- **Typer**: Modern CLI framework with type hints

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please ensure all tests pass and code follows the project's linting rules before submitting a PR.
