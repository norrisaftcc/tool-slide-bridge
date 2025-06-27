# Test Failure Guide

This guide explains what each type of test failure means, why it happens, and how to fix it. Perfect for students and developers learning our CI/CD process.

## Table of Contents

- [Code Quality Failures](#code-quality-failures)
- [Python Test Failures](#python-test-failures)
- [MARP CLI Failures](#marp-cli-failures)
- [Security Scan Failures](#security-scan-failures)
- [Integration Test Failures](#integration-test-failures)

## Code Quality Failures

### Black Formatting Failure

**What this means:**
Your code doesn't follow our standardized Python formatting rules. Black is an opinionated code formatter that ensures consistent style across the entire codebase.

**Example failure:**
```
would reformat src/tool_slide_bridge/cli.py
Oh no! 💥 💔 💥
1 file would be reformatted, 23 files left unchanged.
```

**Why this matters:**
- Consistent formatting makes code easier to read and review
- Reduces cognitive load when switching between files
- Prevents formatting debates in code reviews
- Industry standard practice for professional Python development

**How to fix:**
```bash
# Fix all formatting issues
black src tests

# Preview changes before applying
black --diff src tests

# Check if files need formatting (without changing them)
black --check src tests
```

**Learning opportunity:**
Try deliberately formatting some code "badly" (inconsistent quotes, spacing) then run Black to see how it standardizes everything.

---

### isort Import Failure

**What this means:**
Your Python imports aren't organized according to our standards. The `isort` tool sorts imports alphabetically and groups them logically.

**Example failure:**
```
ERROR: /src/tool_slide_bridge/cli.py Imports are incorrectly sorted and/or formatted.
--- /src/tool_slide_bridge/cli.py:before  2024-01-01 12:00:00.000000
+++ /src/tool_slide_bridge/cli.py:after   2024-01-01 12:00:01.000000
@@ -1,5 +1,5 @@
 import sys
+import random
 from pathlib import Path
-import random
 import click
```

**Why this matters:**
- Organized imports are easier to scan and understand
- Prevents merge conflicts from differently-ordered imports  
- Standard practice follows PEP 8 import ordering guidelines
- Makes it easier to spot missing or duplicate imports

**Import order convention:**
1. Standard library imports (`import os`, `import sys`)
2. Third-party imports (`import click`, `import requests`)
3. Local application imports (`from .converter import MarpConverter`)

**How to fix:**
```bash
# Fix import ordering
isort src tests

# Preview changes
isort --diff src tests

# Check without modifying
isort --check-only src tests
```

---

### Flake8 Linting Failure

**What this means:**
Your code violates Python style guidelines (PEP 8) or has potential bugs that the linter caught.

**Common error codes and meanings:**

#### E501 - Line too long
```
src/cli.py:45:89: E501 line too long (92 > 88 characters)
```
**Why this matters:** Long lines are hard to read, especially on smaller screens or when viewing diffs.

**How to fix:**
```python
# Before (too long)
result = some_very_long_function_name(argument1, argument2, argument3, argument4)

# After (properly wrapped)
result = some_very_long_function_name(
    argument1, argument2, argument3, argument4
)
```

#### F401 - Imported but unused
```
src/cli.py:5:1: F401 'os' imported but unused
```
**Why this matters:** Unused imports clutter the code and may indicate incomplete refactoring.

**How to fix:**
```python
# Remove the unused import
# import os  # <- Delete this line

# Or use it if it was meant to be there
import os
current_dir = os.getcwd()
```

#### E302 - Expected 2 blank lines
```
src/cli.py:15:1: E302 expected 2 blank lines, found 1
```
**Why this matters:** Consistent spacing makes code structure clearer.

**How to fix:**
```python
class MyClass:
    pass

# Need 2 blank lines here (not just 1)

def my_function():
    pass
```

**How to run locally:**
```bash
# Check all files
flake8 src tests

# Check specific file
flake8 src/tool_slide_bridge/cli.py

# Show only specific error types
flake8 src --select=E501,F401
```

---

### Mypy Type Checking Failure

**What this means:**
Python type annotations are missing or incorrect. Mypy helps catch type-related bugs before runtime.

**Common mypy errors:**

#### Missing return type annotation
```
src/cli.py:34: error: Function is missing a return type annotation
```

**Why this matters:**
- Type hints make code self-documenting
- Help IDEs provide better autocomplete and error detection
- Catch type-related bugs early
- Make code more maintainable

**How to fix:**
```python
# Before
def get_message():
    return "Hello World"

# After
def get_message() -> str:
    return "Hello World"

# For functions that don't return anything
def print_banner() -> None:
    print("Banner")
```

#### Type mismatch
```
src/cli.py:42: error: Argument 1 to "int" has incompatible type "str"; expected "Union[str, bytes, SupportsInt]"
```

**How to fix:**
```python
# Before (problematic)
user_input = input("Enter number: ")
result = calculate(user_input)  # calculate expects int

# After (explicit conversion)
user_input = input("Enter number: ")
result = calculate(int(user_input))
```

**How to run locally:**
```bash
# Check all source files
mypy src

# Check specific file
mypy src/tool_slide_bridge/cli.py

# Ignore missing imports (common for third-party packages)
mypy src --ignore-missing-imports
```

---

## Python Test Failures

### Test Function Failure

**What this means:**
One or more of your unit tests is failing. This indicates either:
1. Your code has a bug
2. Your test has incorrect expectations
3. Test setup is wrong

**Example failure:**
```
FAILED tests/test_cli.py::TestFortuneBanner::test_fortune_messages_list_exists - AssertionError: assert [] is not None
```

**Understanding the failure:**
- `FAILED` - Test didn't pass
- `tests/test_cli.py` - File containing the failing test  
- `TestFortuneBanner` - Test class
- `test_fortune_messages_list_exists` - Specific test method
- `AssertionError: assert [] is not None` - What went wrong

**Why this matters:**
- Tests are your safety net against introducing bugs
- Failing tests often indicate real problems in your code
- Good tests document expected behavior
- Green tests give confidence that changes don't break existing functionality

**How to debug:**
```bash
# Run just the failing test
pytest tests/test_cli.py::TestFortuneBanner::test_fortune_messages_list_exists -v

# Run all tests in a file
pytest tests/test_cli.py -v

# Get more detailed output
pytest tests/test_cli.py -v -s

# Stop on first failure
pytest tests/test_cli.py -x
```

**Common causes and fixes:**

#### Assertion Error
```python
# Test expects this:
assert len(FORTUNE_MESSAGES) > 0

# But code has:
FORTUNE_MESSAGES = []  # Empty list!

# Fix by adding messages to the list
FORTUNE_MESSAGES = ["Message 1", "Message 2"]
```

#### Import Error
```
ImportError: cannot import name 'print_banner' from 'tool_slide_bridge.cli'
```
- Function doesn't exist or is named differently
- Module path is wrong
- Missing `__init__.py` file

---

### Test Coverage Failure

**What this means:**
Less than 80% of your code is covered by tests. This suggests some code paths aren't being tested.

**Example failure:**
```
FAIL Required test coverage of 80% not reached. Total coverage: 75.32%
```

**Why this matters:**
- Untested code is more likely to contain bugs
- High coverage gives confidence in refactoring
- Industry best practice for maintaining code quality
- Helps identify dead code or complex logic that needs testing

**How to investigate:**
```bash
# See overall coverage
pytest --cov=tool_slide_bridge --cov-report=term-missing

# Generate HTML report for detailed analysis
pytest --cov=tool_slide_bridge --cov-report=html
# Open htmlcov/index.html in browser

# See which lines aren't covered
pytest --cov=tool_slide_bridge --cov-report=term-missing | grep TOTAL
```

**Coverage report interpretation:**
```
Name                           Stmts   Miss  Cover   Missing
----------------------------------------------------------
src/tool_slide_bridge/cli.py     45      8    82%   23-25, 67-70
```
- `Stmts`: Total statements in file
- `Miss`: Statements not covered by tests
- `Cover`: Percentage covered
- `Missing`: Line numbers not covered

**How to improve coverage:**
1. **Write tests for uncovered lines**:
   ```python
   # If lines 23-25 handle error cases:
   def test_error_handling():
       with pytest.raises(ValueError):
           problematic_function("bad_input")
   ```

2. **Test different code paths**:
   ```python
   # Test both if/else branches
   def test_condition_true():
       result = my_function(True)
       assert result == "expected_for_true"
   
   def test_condition_false():
       result = my_function(False)
       assert result == "expected_for_false"
   ```

3. **Remove dead code** if it's genuinely unused

---

## MARP CLI Failures

### MARP Installation Check Failure

**What this means:**
The MARP CLI (Markdown Presentation Ecosystem) isn't installed or accessible in the CI environment.

**Example failure:**
```
/bin/sh: marp: command not found
Error: Process completed with exit code 127.
```

**Why this matters:**
- MARP is essential for converting Markdown to presentations
- Installation issues prevent the core functionality from working
- Node.js and npm ecosystem differences between environments

**How to debug locally:**
```bash
# Check if MARP is installed
marp --version

# Install globally if missing
npm install -g @marp-team/marp-cli

# Check npm global bin directory
npm bin -g

# Ensure it's in PATH
export PATH="$PATH:$(npm bin -g)"
```

**Common causes:**
1. **Node.js version incompatibility**
2. **npm permissions issues**
3. **Global package installation problems**
4. **PATH environment variable issues**

---

### MARP Conversion Failure

**What this means:**
MARP CLI runs but fails to convert Markdown to the desired output format.

**Example failure:**
```
Error: Could not read theme: themes/corporate.css
Error: Conversion failed
```

**Why this matters:**
- Indicates problems with Markdown syntax or theme files
- May prevent successful presentation generation
- Could indicate missing dependencies or assets

**Common causes and fixes:**

#### Theme file missing or invalid
```bash
# Check if theme exists
ls themes/corporate.css

# Test with default theme
marp input.md --theme default -o output.html

# Validate CSS syntax in custom theme
```

#### Invalid Markdown frontmatter
```markdown
---
marp: true
theme: corporate  # Must match existing theme
---
# Your slides here
```

#### File path issues
```bash
# Use absolute paths
marp /full/path/to/input.md -o /full/path/to/output.html

# Check working directory
pwd
ls -la
```

---

## Security Scan Failures

### Safety (Dependency Vulnerability) Failure

**What this means:**
One or more Python dependencies have known security vulnerabilities.

**Example failure:**
```
vulnerabilities found:
 requests==2.25.1 has known vulnerabilities:
 - ID: 51499 - Request library has a potential security vulnerability
```

**Why this matters:**
- Vulnerable dependencies can be exploited by attackers
- Security is everyone's responsibility
- Keeping dependencies updated is basic software hygiene
- Compliance requirements in professional environments

**How to fix:**
```bash
# Check for vulnerabilities locally
safety check --file requirements.txt

# Update vulnerable package
pip install --upgrade requests

# Update requirements.txt with new version
pip freeze > requirements.txt

# Or update specific package in requirements.txt
# requests==2.28.2  # Replace with newer version
```

**Prevention:**
- Regularly update dependencies
- Use dependabot for automated security updates
- Monitor security advisories for your dependencies

---

### Bandit (Security Linting) Failure

**What this means:**
Static analysis found potential security issues in your Python code.

**Example failure:**
```
Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'secret123'
Severity: Medium   Confidence: Medium
Location: src/cli.py:15
```

**Common security issues:**

#### B105 - Hardcoded passwords
```python
# Bad
password = "secret123"

# Good
password = os.environ.get("PASSWORD")
```

#### B311 - Insecure random
```python
# Bad - predictable for security purposes
import random
token = random.randint(1000, 9999)

# Good - cryptographically secure
import secrets
token = secrets.randbelow(9999)
```

#### B601 - Shell injection
```python
# Bad - user input could be malicious
os.system(f"ls {user_input}")

# Good - use subprocess with list
subprocess.run(["ls", user_input])
```

**Why this matters:**
- Security vulnerabilities can lead to data breaches
- Prevention is much cheaper than remediation
- Professional software must follow security best practices

---

## Integration Test Failures

### End-to-End Workflow Failure

**What this means:**
The complete workflow from input to output isn't working correctly.

**Example failure:**
```
AssertionError: Expected output file 'presentation.pptx' to exist
```

**Why this matters:**
- Integration tests verify that all components work together
- Catches issues that unit tests might miss
- Simulates real user experience
- Essential for deployment confidence

**How to debug:**
1. **Check intermediate outputs**:
   ```bash
   # Look for intermediate files that should be created
   ls -la presentations/
   ls -la *.md
   ```

2. **Run components individually**:
   ```bash
   # Test MARP conversion separately
   marp input.md -o test.html
   
   # Test Python parts separately
   python -c "from tool_slide_bridge.cli import main; main()"
   ```

3. **Check error logs**:
   - Look for stack traces in CI logs
   - Check for missing environment variables
   - Verify all dependencies are installed

**Common integration issues:**
- **File path mismatches** between components
- **Missing environment setup** (MARP not installed)
- **Permission issues** writing output files
- **Resource constraints** in CI environment

---

## Debugging Strategy

When any test fails, follow this systematic approach:

### 1. Understand the Error
- Read the complete error message
- Identify which specific test/check failed
- Note any error codes or specific line numbers

### 2. Reproduce Locally
```bash
# Use the exact same commands as CI
black --check src tests
isort --check-only src tests
flake8 src tests
mypy src
pytest tests/ -v
```

### 3. Isolate the Problem
- Run just the failing test/check
- Test with minimal inputs
- Check if it's environment-specific

### 4. Fix and Verify
- Make the necessary changes
- Run the test again locally
- Ensure you didn't break anything else

### 5. Learn from the Failure
- Understand why the issue occurred
- Consider how to prevent similar issues
- Update documentation if needed

## Getting Help

If you're stuck after following this guide:

1. **Check recent similar failures** in other PRs
2. **Post detailed error info** in PR comments
3. **Include steps you've already tried**
4. **Ask specific questions** rather than "it doesn't work"

Remember: Every test failure is a learning opportunity! Understanding these failures makes you a better developer and helps improve our codebase quality.