# Contributing to AICodeGen

Thank you for your interest in contributing to AICodeGen! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of AI/ML concepts
- Familiarity with code generation techniques

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AICodeGen.git
   cd AICodeGen
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## 🛠️ Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 2. Make Changes

- Write clean, readable code
- Follow existing code style and patterns
- Add appropriate tests
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aicodegen --cov-report=html

# Run linting
flake8 aicodegen/
pylint aicodegen/

# Format code
black aicodegen/
isort aicodegen/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new code generation feature"
```

#### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Maximum line length: 88 characters (Black default)

### Code Structure

```python
"""Module docstring describing the purpose."""

import standard_library
import third_party_library

from aicodegen import local_module


class ExampleClass:
    """Class docstring with description.
    
    Attributes:
        attribute_name: Description of the attribute.
    """
    
    def __init__(self, param: str) -> None:
        """Initialize the class.
        
        Args:
            param: Description of the parameter.
        """
        self.attribute_name = param
    
    def public_method(self, arg: int) -> str:
        """Public method with clear documentation.
        
        Args:
            arg: Description of the argument.
            
        Returns:
            Description of the return value.
            
        Raises:
            ValueError: When input is invalid.
        """
        return self._private_method(arg)
    
    def _private_method(self, arg: int) -> str:
        """Private method for internal use."""
        if arg < 0:
            raise ValueError("Argument must be non-negative")
        return str(arg)
```

### Documentation Standards

- Use Google-style docstrings
- Document all public APIs
- Include type hints for all functions
- Add examples in docstrings for complex functions

## 🧪 Testing Guidelines

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

from aicodegen.generator import CodeGenerator


class TestCodeGenerator:
    """Test suite for CodeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.generator = CodeGenerator()
    
    def test_generate_basic_function(self):
        """Test basic function generation."""
        result = self.generator.generate(
            description="Create a hello world function",
            language="python"
        )
        
        assert "def" in result
        assert "hello" in result.lower()
    
    def test_generate_with_invalid_language(self):
        """Test error handling for invalid language."""
        with pytest.raises(ValueError, match="Unsupported language"):
            self.generator.generate(
                description="Test",
                language="invalid_language"
            )
    
    @patch('aicodegen.models.llm_client')
    def test_generate_with_mocked_llm(self, mock_client):
        """Test generation with mocked LLM client."""
        mock_client.return_value = "def hello():\n    return 'Hello, World!'"
        
        result = self.generator.generate(
            description="Hello function",
            language="python"
        )
        
        assert result == "def hello():\n    return 'Hello, World!'"
        mock_client.assert_called_once()
```

### Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test performance characteristics

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Minimal steps to reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, package versions
6. **Code Sample**: Minimal code that reproduces the issue

### Bug Report Template

```markdown
## Bug Description
Brief description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- AICodeGen: [e.g., 1.2.3]

## Code Sample
```python
# Minimal code that reproduces the issue
```

## Additional Context
Any other context about the problem.
```

## 💡 Feature Requests

When requesting features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for solving it
3. **Alternatives**: Other solutions you've considered
4. **Implementation**: Ideas about how it could be implemented

## 🔍 Code Review Process

### For Contributors

- Keep PRs focused and atomic
- Write clear PR descriptions
- Respond to feedback promptly
- Update tests and documentation

### For Reviewers

- Be constructive and helpful
- Focus on code quality and maintainability
- Suggest improvements, not just problems
- Approve when ready, request changes when needed

## 📋 PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] Tests are added/updated and passing
- [ ] Documentation is updated if needed
- [ ] Commit messages follow convention
- [ ] PR description clearly explains changes
- [ ] No merge conflicts exist
- [ ] CI/CD checks are passing

## 🏷️ Labels and Milestones

### Common Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

### Priority Labels

- `priority/critical` - Critical issues
- `priority/high` - High priority
- `priority/medium` - Medium priority
- `priority/low` - Low priority

## 🌟 Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation
- Social media shout-outs for major contributions

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **Discord**: Join our [Discord server](https://discord.gg/aicodegen)
- **Email**: Reach out to maintainers@aicodegen.dev

## 📜 License

By contributing to AICodeGen, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AICodeGen! 🚀