# CI/CD Guide - Tool Slide Bridge

This guide explains our continuous integration (CI) process, what each check does, and how to troubleshoot failures.

## Overview

We use GitHub Actions for our CI/CD pipeline with three main workflows:

1. **Continuous Integration (CI)** - Runs on every push and PR
2. **Release** - Handles versioned releases and PyPI publishing
3. **Security** - Daily security scans and vulnerability checks

## CI Workflow Components

### 1. Code Quality Checks (Lint & Format)

These checks ensure consistent code style and catch common errors.

#### What runs:
- **Black** - Python code formatter
- **isort** - Python import sorter
- **flake8** - Python linter
- **mypy** - Python type checker

#### Common failures and fixes:

**Black formatting error:**
```bash
# Error: "would reformat src/tool_slide_bridge/cli.py"
# Fix locally:
black src tests
```

**isort import order error:**
```bash
# Error: "Imports are incorrectly sorted"
# Fix locally:
isort src tests
```

**flake8 linting error:**
```bash
# Error: "E501 line too long (92 > 88 characters)"
# Fix: Break long lines or configure in pyproject.toml
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
```

**mypy type error:**
```bash
# Error: "error: Function is missing a return type annotation"
# Fix: Add type annotations
mypy src --ignore-missing-imports
```

### 2. Python Tests

Tests run across multiple Python versions (3.9-3.13) and operating systems.

#### What runs:
- Unit tests with pytest
- Code coverage check (minimum 80%)
- Multi-OS testing (Ubuntu, Windows, macOS)

#### Common failures and fixes:

**Test failure:**
```bash
# Run tests locally to reproduce:
pytest tests/ -v

# Run specific test:
pytest tests/test_cli.py::TestFortuneBanner::test_fortune_messages_list_exists -v
```

**Coverage below threshold:**
```bash
# Error: "Coverage failure: total coverage is 75.00%, below threshold of 80%"
# Check coverage locally:
pytest --cov=tool_slide_bridge --cov-report=term-missing

# See which lines aren't covered:
pytest --cov=tool_slide_bridge --cov-report=html
# Open htmlcov/index.html in browser
```

**OS-specific failure:**
- Windows: Often path separator issues (`/` vs `\`)
- macOS: May have different system libraries
- Solution: Use `pathlib.Path` for cross-platform paths

### 3. MARP CLI Tests

Tests the MARP (Markdown Presentation) CLI integration.

#### What runs:
- MARP CLI installation check
- Basic MARP conversion test
- Theme validation

#### Common failures and fixes:

**MARP not installed:**
```bash
# Install globally:
npm install -g @marp-team/marp-cli

# Verify installation:
marp --version
```

**MARP conversion failure:**
```bash
# Test locally:
marp tests/fixtures/test.md --html -o presentations/test.html
```

### 4. Integration Tests

End-to-end tests of the complete workflow.

#### What runs:
- Full tool workflow tests
- Multi-component interaction tests

Currently placeholder - will be expanded as features are implemented.

### 5. Security Scans

Automated security checks for vulnerabilities.

#### What runs:
- **Safety** - Python dependency vulnerabilities
- **Bandit** - Python security linting
- **CodeQL** - Static code analysis
- **npm audit** - Node.js dependency vulnerabilities

#### Common issues:

**Vulnerable dependency:**
```bash
# Check Python dependencies:
safety check --file requirements.txt

# Update specific package:
pip install --upgrade package-name
```

**Security code issue:**
```bash
# Run Bandit locally:
bandit -r src/

# Common issues:
# - Hardcoded passwords (B105)
# - Use of eval() (B307)
# - Insecure random (B311)
```

## Local Development Setup

To match the CI environment locally:

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements-dev.txt

# Node.js dependencies
npm install
npm install -g @marp-team/marp-cli
```

### 2. Pre-commit Hooks

Set up pre-commit to catch issues before pushing:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### 3. Run All Checks Locally

Create a script to run all CI checks:

```bash
#!/bin/bash
# save as: scripts/run-ci-checks.sh

echo "Running CI checks locally..."

# Code quality
echo "1. Running Black..."
black --check src tests

echo "2. Running isort..."
isort --check-only src tests

echo "3. Running flake8..."
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

echo "4. Running mypy..."
mypy src --ignore-missing-imports

# Tests
echo "5. Running tests with coverage..."
pytest tests/ -v --cov=tool_slide_bridge --cov-report=term-missing

# Security
echo "6. Running security checks..."
safety check --file requirements.txt
bandit -r src/

echo "All checks complete!"
```

## Debugging CI Failures

### 1. Understanding the Error

1. Click on the failing check in the PR
2. Find the specific step that failed
3. Look for error messages in red

### 2. Reproduce Locally

Always try to reproduce CI failures locally first:

```bash
# Check Python version
python --version

# Create clean virtual environment
python -m venv venv_test
source venv_test/bin/activate  # or venv_test\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-dev.txt

# Run the failing command
```

### 3. Common CI-Only Issues

**Different Python version:**
```bash
# Test with specific Python version using pyenv or conda
pyenv install 3.9.18
pyenv local 3.9.18
```

**Missing system dependencies:**
- CI runs on clean Ubuntu/Windows/macOS
- May need to install system packages

**Environment variables:**
- CI has different env vars than local
- Check workflow file for `env:` sections

**File permissions:**
- CI may have different permissions
- Especially important for scripts

### 4. Viewing Artifacts

Failed CI runs often produce artifacts:

1. Go to Actions tab
2. Click on the failed run
3. Scroll to "Artifacts" section
4. Download reports (coverage, security, etc.)

## CI Performance Tips

### 1. Use Caching

Our CI caches:
- Python pip packages
- Node.js npm packages

Cache keys are based on dependency file hashes.

### 2. Parallel Jobs

- Tests run in parallel across Python versions
- Different checks run as separate jobs
- Use matrix strategy for variants

### 3. Skip Unnecessary Runs

Add `[skip ci]` to commit message to skip CI:
```bash
git commit -m "Update documentation [skip ci]"
```

## Release Process

The release workflow triggers on version tags:

```bash
# Create release
git tag v1.0.0
git push origin v1.0.0

# Pre-release
git tag v1.0.0-beta1
git push origin v1.0.0-beta1
```

## Security Workflow

Runs daily at 2 AM UTC and includes:

1. Dependency vulnerability scanning
2. Static code analysis
3. CodeQL analysis
4. Security compliance checks

View security alerts in:
- GitHub Security tab
- Pull request checks
- Downloaded artifacts

## Getting Help

1. **CI Failure**: First check this guide
2. **Still stuck**: Check recent similar PRs
3. **Need help**: 
   - Post in PR comments with error details
   - Tag @norrisaftcc for infrastructure issues
   - Create issue for persistent CI problems

## Workflow Files

- `.github/workflows/ci.yml` - Main CI checks
- `.github/workflows/release.yml` - Release automation
- `.github/workflows/security.yml` - Security scanning

Each workflow file contains inline comments explaining steps.