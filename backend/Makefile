.PHONY: help install lint format type-check test clean lint-fix format-fix

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync --dev

lint: ## Run linting checks (flake8 only)
	uv run flake8 app/

format-check: ## Check code formatting (black + isort)
	uv run black --check app/
	uv run isort --check-only app/

type-check: ## Run type checking (mypy)
	uv run mypy app/ --ignore-missing-imports

check-all: lint format-check type-check ## Run all checks (lint + format + type)

analyze-lengths: ## Analyze function and file lengths
	uv run python scripts/lint_analysis.py

check-comprehensive: check-all analyze-lengths ## Run comprehensive checks including length analysis

format-fix: ## Fix formatting issues (black + isort)
	uv run black app/
	uv run isort app/

lint-fix: ## Fix auto-fixable linting issues
	uv run black app/
	uv run isort app/
	uv run flake8 app/ --extend-ignore=E501,W503,E203

test: ## Run tests
	uv run pytest -v

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.pyc" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

pre-commit: ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

# CI/CD helper
ci: install check-all test ## Run full CI pipeline (install + check + test)
