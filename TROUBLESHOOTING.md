# Troubleshooting Guide

This guide helps you resolve common issues with tool-slide-bridge development and CI/CD.

## Quick Links

- [CI Failures](#ci-failures)
- [Local Development Issues](#local-development-issues)
- [MARP Issues](#marp-issues)
- [Python Environment Issues](#python-environment-issues)
- [Testing Issues](#testing-issues)

## CI Failures

### Black Formatting Failed

**Error:**
```
would reformat src/tool_slide_bridge/cli.py
Oh no! 💥 💔 💥
1 file would be reformatted
```

**Solution:**
```bash
# Fix locally
black src tests

# Check what would change
black --diff src tests

# Commit the formatted files
git add -u
git commit -m "Apply Black formatting"
```

### isort Import Order Failed

**Error:**
```
ERROR: /src/tool_slide_bridge/cli.py Imports are incorrectly sorted and/or formatted.
```

**Solution:**
```bash
# Fix locally
isort src tests

# Check what would change
isort --diff src tests

# Fix and verify
isort src tests && isort --check-only src tests
```

### Flake8 Linting Failed

**Error Examples:**
```
E501 line too long (92 > 88 characters)
F401 'module.name' imported but unused
E302 expected 2 blank lines, found 1
```

**Solutions:**

1. **Line too long (E501)**:
   ```python
   # Before
   very_long_line = "This is a very long string that exceeds the maximum line length limit"
   
   # After
   very_long_line = (
       "This is a very long string that "
       "exceeds the maximum line length limit"
   )
   ```

2. **Unused import (F401)**:
   ```python
   # Remove the unused import or use it
   # Or add # noqa: F401 if intentionally unused
   from typing import Optional  # noqa: F401
   ```

3. **Blank lines (E302)**:
   ```python
   # Add required blank lines between class/function definitions
   class MyClass:
       pass
   
   
   def my_function():  # Note: 2 blank lines before
       pass
   ```

### Mypy Type Checking Failed

**Error Examples:**
```
error: Function is missing a return type annotation
error: Argument 1 to "function" has incompatible type "str"; expected "int"
```

**Solutions:**

1. **Missing return type**:
   ```python
   # Before
   def get_message():
       return "Hello"
   
   # After
   def get_message() -> str:
       return "Hello"
   ```

2. **Type mismatch**:
   ```python
   # Before
   process_number("123")  # expects int
   
   # After
   process_number(int("123"))
   ```

### Test Coverage Below 80%

**Error:**
```
FAIL Required test coverage of 80% not reached. Total coverage: 75.32%
```

**Solution:**
```bash
# See what's not covered
pytest --cov=tool_slide_bridge --cov-report=term-missing

# Generate HTML report
pytest --cov=tool_slide_bridge --cov-report=html
# Open htmlcov/index.html

# Write tests for uncovered code
```

### Test Failures

**Common patterns:**

1. **Import errors**:
   ```
   ImportError: cannot import name 'module' from 'package'
   ```
   - Check if `__init__.py` exists
   - Verify PYTHONPATH includes src directory

2. **Assertion failures**:
   ```
   AssertionError: assert 'expected' == 'actual'
   ```
   - Run specific test locally
   - Check test assumptions

3. **Mock failures**:
   ```
   AssertionError: Expected 'mock' to be called once. Called 0 times.
   ```
   - Verify mock setup
   - Check if code path is executed

## Local Development Issues

### Virtual Environment Problems

**Issue:** Package conflicts or wrong Python version

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv_fresh
source venv_fresh/bin/activate  # Linux/Mac
# or
venv_fresh\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'tool_slide_bridge'`

**Solution:**
```bash
# Install package in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Permission Errors

**Issue:** Permission denied when running scripts

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with interpreter
python scripts/script.py
bash scripts/script.sh
```

## MARP Issues

### MARP CLI Not Found

**Error:**
```
marp: command not found
```

**Solution:**
```bash
# Install globally
npm install -g @marp-team/marp-cli

# Or use npx
npx @marp-team/marp-cli --version

# Add to PATH if needed
export PATH="$PATH:$(npm bin -g)"
```

### MARP Conversion Fails

**Issue:** MARP doesn't generate output

**Debug steps:**
1. Check markdown syntax:
   ```markdown
   ---
   marp: true
   theme: default
   ---
   # Slide 1
   ```

2. Test with simple file:
   ```bash
   echo "# Test" | marp - -o test.html
   ```

3. Check theme exists:
   ```bash
   ls themes/
   marp --theme themes/corporate.css input.md
   ```

### Node.js Version Issues

**Error:** `npm ERR! engine Unsupported engine`

**Solution:**
```bash
# Check Node version
node --version

# Install correct version with nvm
nvm install 18
nvm use 18
```

## Python Environment Issues

### Multiple Python Versions

**Issue:** Wrong Python version active

**Solution with pyenv:**
```bash
# Install Python version
pyenv install 3.11.8
pyenv local 3.11.8

# Verify
python --version
```

**Solution with conda:**
```bash
conda create -n tool-slide python=3.11
conda activate tool-slide
```

### Dependency Conflicts

**Error:** `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**Solution:**
```bash
# Use fresh virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

## Testing Issues

### Pytest Not Finding Tests

**Issue:** `collected 0 items`

**Solution:**
```bash
# Ensure test files follow naming convention
# test_*.py or *_test.py

# Run from project root
pytest tests/

# Specify test path explicitly
pytest tests/test_cli.py
```

### Mock/Patch Issues

**Issue:** Mocks not working as expected

**Common solutions:**

1. **Wrong patch target**:
   ```python
   # Wrong
   @patch('random.choice')
   
   # Right - patch where it's used
   @patch('tool_slide_bridge.cli.random.choice')
   ```

2. **Import vs from import**:
   ```python
   # If code uses: import random
   @patch('tool_slide_bridge.cli.random')
   
   # If code uses: from random import choice
   @patch('tool_slide_bridge.cli.choice')
   ```

### Async Test Issues

**Issue:** Async tests failing

**Solution:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

## Platform-Specific Issues

### Windows Path Issues

**Issue:** Tests fail on Windows due to path separators

**Solution:**
```python
# Use pathlib
from pathlib import Path

# Wrong
file_path = "src/module/file.py"

# Right
file_path = Path("src") / "module" / "file.py"
```

### macOS SSL Certificate Issues

**Issue:** SSL certificate verification failed

**Solution:**
```bash
# Install certificates
pip install --upgrade certifi

# Or for homebrew Python
brew install ca-certificates
```

### Linux Missing System Dependencies

**Issue:** Package installation fails

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Fedora/RHEL
sudo dnf install python3-devel gcc
```

## Quick Fixes Checklist

When CI fails, try these in order:

1. **Pull latest main**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Run formatters**:
   ```bash
   black src tests
   isort src tests
   ```

3. **Run linters**:
   ```bash
   flake8 src tests
   mypy src
   ```

4. **Run tests**:
   ```bash
   pytest tests/
   ```

5. **Check dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   npm install
   ```

## Getting More Help

If these solutions don't work:

1. **Check CI logs**: Click through to the specific failing step
2. **Search issues**: Similar problem may be already reported
3. **Ask for help**: Include:
   - Exact error message
   - Steps to reproduce
   - Environment details (OS, Python version)
   - What you've already tried

## Useful Commands Reference

```bash
# Format code
black src tests
isort src tests

# Check code quality
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
mypy src --ignore-missing-imports

# Run tests
pytest tests/ -v
pytest tests/ -v --cov=tool_slide_bridge --cov-report=term-missing

# Security checks
safety check --file requirements.txt
bandit -r src/

# Clean up
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
```