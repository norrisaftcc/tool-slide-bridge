# Contributing to Tool Slide Bridge

Thank you for your interest in contributing to Tool Slide Bridge! This document provides guidelines and information for contributors following SAFE, FLOW, and VIBE methodologies.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [SAFE/FLOW Process](#safeflow-process)
- [VIBE Standards](#vibe-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.9+ and pip
- Node.js 16+ and npm
- Git
- Basic knowledge of PowerPoint/presentation formats

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tool-slide-bridge.git
   cd tool-slide-bridge
   ```

2. **Set up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Install MARP CLI**
   ```bash
   npm install -g @marp-team/marp-cli
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   pytest tests/
   marp --version
   ```

## Development Workflow

We follow the **FLOW** (Follow Logical Work Order) methodology:

### 1. Issue-Driven Development
- All work must start with a GitHub issue
- Use appropriate issue templates (Epic, Feature, Bug, Tech Debt)
- Get issue approved before starting work

### 2. Branch Strategy
- `main` - Production ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### 3. Logical Work Order
1. **Plan** → Create/refine issue with acceptance criteria
2. **Design** → Technical design and architecture decisions
3. **Implement** → Write code following VIBE standards
4. **Test** → Comprehensive testing (unit, integration, manual)
5. **Review** → Peer code review
6. **Deploy** → Merge and release

## SAFE/FLOW Process

### Epics and Features
- **Epic**: Large business initiative (multiple sprints)
- **Feature**: Deliverable functionality (1-2 sprints)
- **Story**: Specific user-focused functionality (1-5 days)

### Definition of Done
- [ ] Code implemented and follows style guidelines
- [ ] Unit tests written with ≥80% coverage
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance impact assessed
- [ ] Manual testing completed
- [ ] Peer review approved

### Value Stream
1. **Ideation** → Issues created with business value
2. **Development** → Implementation following VIBE
3. **Validation** → Testing and quality assurance
4. **Deployment** → Release to users

## VIBE Standards

**VIBE** = Verification Inspires Behavior Examples

### Verification
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Manual Tests**: User workflow validation
- **Automated CI/CD**: Continuous verification

### Behavior
- Write tests that describe expected behavior
- Use Given/When/Then format for acceptance criteria
- Document edge cases and error conditions
- Ensure predictable, reliable functionality

### Examples
- Provide concrete examples in tests
- Include usage examples in documentation
- Create sample presentations and templates
- Demonstrate both success and failure cases

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Write tests for new functionality
   - Update documentation

3. **Commit Changes**
   ```bash
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commit format:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Build process, dependencies

4. **Push Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use the PR template
   - Link to related issues
   - Complete VIBE checklist
   - Request reviewers

### PR Review Criteria
- [ ] VIBE verification checklist completed
- [ ] All CI/CD checks passing
- [ ] Code follows project style guidelines
- [ ] Tests provide adequate coverage
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)

## Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data and samples
└── conftest.py     # Pytest configuration
```

### Test Categories
- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Component interaction tests
- **End-to-End Tests**: Full workflow tests
- **Performance Tests**: Load and performance validation

### Writing Tests
```python
def test_feature_behavior():
    """Test that feature behaves correctly given specific input."""
    # Given
    input_data = create_test_input()
    
    # When  
    result = function_under_test(input_data)
    
    # Then
    assert result.meets_expectations()
```

## Code Style

### Python
- **Formatter**: Black (line length: 88)
- **Import Sorting**: isort
- **Linting**: flake8
- **Type Checking**: mypy
- **Docstrings**: Google style

### JavaScript
- **Formatter**: Prettier
- **Linting**: ESLint
- **Style**: Airbnb configuration

### Documentation
- **Format**: Markdown
- **API Docs**: Sphinx with autodoc
- **Examples**: Include working code examples

## Project Structure

```
tool-slide-bridge/
├── src/tool_slide_bridge/     # Main package
│   ├── marp_converter.py      # MARP integration
│   ├── content_analyzer.py    # Content analysis
│   ├── pptx_builder.py        # Python-PPTX integration
│   └── hybrid_processor.py    # Intelligent routing
├── tests/                     # Test suite
├── themes/                    # MARP themes
├── templates/                 # PowerPoint templates
├── presentations/             # Generated outputs
├── web/                       # React web interface
└── docs/                      # Documentation
```

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a Bug Report issue
- **Features**: Create a Feature Request issue
- **Security**: Email security@example.com

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for helping make Tool Slide Bridge better! 🚀