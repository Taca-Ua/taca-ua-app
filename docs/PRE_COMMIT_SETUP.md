# Pre-commit Setup Guide

This guide walks you through the installation and configuration of pre-commit hooks for the TACA-UA project.

## What is Pre-commit?

Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. It helps ensure code quality by running checks before each commit.

## Installation Steps

### Step 1: Install Pre-commit

Since this project uses Python, pre-commit was installed in the project's virtual environment:

```bash
# Navigate to project directory
cd taca-ua-app

# Install pre-commit in the virtual environment
pip install pre-commit
```

### Step 2: Install Pre-commit Hooks

After installing pre-commit, install the Git hooks:

```bash
pre-commit install
```

This command installs the pre-commit script in your Git repository's `.git/hooks/pre-commit` file.

### Step 3: Configuration

The project includes a `.pre-commit-config.yaml` file with the following hooks:

#### General Hooks
- **conventional-pre-commit**: Ensures commit messages follow the conventional commit format

#### Python-specific Hooks
- **ruff**: Fast Python linter and code formatter (with automatic fixing)
- **black**: Python code formatter
- **isort**: Python import sorter

## Usage

### Automatic Execution

Pre-commit hooks will automatically run when you make a commit:

```bash
git add .
git commit -m "feat: add new feature"
```

If any hook fails, the commit will be aborted, and you'll need to fix the issues before committing again.

### Manual Execution

You can run pre-commit hooks manually on all files:

```bash
pre-commit run --all-files
```

Or run specific hooks:

```bash
pre-commit run ruff
pre-commit run black
```

### Skipping Hooks

If you need to skip pre-commit hooks (not recommended), use:

```bash
git commit -m "commit message" --no-verify
```

## Conventional Commit Format

The conventional-pre-commit hook enforces commit message format. Valid formats include:

- `feat: add new feature`
- `fix: resolve bug in authentication`
- `docs: update README`
- `style: format code with black`
- `refactor: restructure user service`
- `test: add unit tests for user model`
- `chore: update dependencies`

## Troubleshooting

### Common Issues

1. **Hook installation fails**: Ensure you have Git installed and you're in a Git repository
2. **Python hooks fail**: Make sure you're using the correct Python environment
3. **Ruff errors**: The configuration includes `--fix` to automatically fix many issues

### Updating Hooks

To update to the latest versions:

```bash
pre-commit autoupdate
```

### Bypassing Specific Files

You can exclude files from hooks by adding them to the hook configuration or using `.gitignore` patterns.

## Benefits

- **Code Quality**: Automated linting and formatting ensure consistent code style
- **Commit Standards**: Conventional commits improve project history and enable automated changelog generation
- **Early Detection**: Catch issues before they reach the repository
- **Team Consistency**: All team members follow the same code standards

---

For more information about pre-commit, visit: https://pre-commit.com/
