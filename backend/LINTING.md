# Linting and Code Quality

This project uses a comprehensive linting setup to maintain code quality, consistency, and readability.

## Tools Configured

### 🔧 **Black** - Code Formatter
- **Purpose**: Automatic code formatting
- **Line length**: 88 characters
- **Target version**: Python 3.10+
- **Usage**: `uv run black app/`

### 📋 **isort** - Import Sorter
- **Purpose**: Automatic import sorting and formatting
- **Profile**: Black-compatible
- **Line length**: 88 characters
- **Usage**: `uv run isort app/`

### 🔍 **flake8** - Linter
- **Purpose**: Code quality and style checking
- **Line length**: 88 characters
- **Complexity limit**: 10
- **File length limit**: 300 lines
- **Function length limit**: 50 lines
- **Usage**: `uv run flake8 app/`

### 🏷️ **mypy** - Type Checker
- **Purpose**: Static type checking
- **Python version**: 3.10
- **Strict mode**: Enabled with appropriate overrides
- **Usage**: `uv run mypy app/ --ignore-missing-imports`

## Length Limits

### File Length: 300 lines
- Prevents monolithic files
- Encourages modular design
- Files exceeding this limit should be split into logical modules

### Function Length: 50 lines
- Promotes focused, single-responsibility functions
- Improves readability and testability
- Functions exceeding this limit should be broken down

## Usage

### Quick Commands

```bash
# Install all linting tools
make install

# Run all checks (lint + format + type)
make check-all

# Run comprehensive checks including length analysis
make check-comprehensive

# Fix formatting issues automatically
make format-fix

# Run only linting checks
make lint

# Check formatting without fixing
make format-check

# Run type checking
make type-check

# Analyze function and file lengths
make analyze-lengths
```

### Pre-commit Hooks

Pre-commit hooks are configured to automatically run before each commit:

```bash
# Install pre-commit hooks
make pre-commit-install

# Run pre-commit manually on all files
make pre-commit
```

The pre-commit hooks will:
1. Check for trailing whitespace and formatting issues
2. Run Black to format code
3. Run isort to sort imports
4. Run flake8 for linting
5. Run mypy for type checking

## Configuration Files

- **`pyproject.toml`**: All tool configurations
- **`.pre-commit-config.yaml`**: Pre-commit hook setup
- **`scripts/lint_analysis.py`**: Custom length analysis script

## Common Issues and Solutions

### Function Too Long
If a function exceeds 50 lines:
1. Extract helper methods for complex logic
2. Break down into smaller, focused functions
3. Consider creating a separate class if the function has multiple responsibilities

### File Too Long
If a file exceeds 300 lines:
1. Split into logical modules
2. Extract related functionality into separate files
3. Consider creating a package for complex modules

### Type Errors
If mypy reports type errors:
1. Add type annotations to function signatures
2. Use `-> None` for functions that don't return values
3. Import types from `typing` module as needed

### Import Sorting
isort will automatically:
1. Group imports into standard library, third-party, and local imports
2. Sort imports alphabetically within each group
3. Remove duplicate imports

## Best Practices

1. **Run linting before committing**: Always run `make check-comprehensive` before committing
2. **Fix issues incrementally**: Address linting issues as you work, not all at once
3. **Use meaningful function names**: Short functions should have descriptive names
4. **Add docstrings**: All public functions and classes should have docstrings
5. **Keep functions focused**: Each function should do one thing well
6. **Write tests**: Test coverage helps catch refactoring issues

## IDE Integration

Most IDEs can integrate these tools:

### VS Code
Install these extensions:
- Python (Microsoft)
- Black Formatter
- isort
- flake8
- mypy

Configure in `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true
}
```

### PyCharm
- Configure Black as external formatter
- Enable isort in settings
- Set up flake8 and mypy as external tools

## Continuous Integration

The linting setup is designed to work well with CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run linting
  run: |
    cd backend
    make check-comprehensive
```

This ensures all code meets quality standards before merging.
