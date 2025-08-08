# Contributing to AICodeGen

Thank you for your interest in contributing to AICodeGen! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key (for testing AI features)

### Setting up the Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/ksjpswaroop/AICodeGen.git
   cd AICodeGen
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   export AICODEGEN_DEBUG="true"
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aicodegen

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfig::test_default_config
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/aicodegen/
```

### Testing Your Changes

1. **Unit Tests**: Add tests for new functionality
2. **Integration Tests**: Test CLI commands and workflows
3. **Manual Testing**: Use the demo script to verify features

```bash
# Run the demo
python demo.py

# Test CLI commands
aicodegen --help
aicodegen config-show
aicodegen analyze src/aicodegen/core/config.py
```

## Contributing Guidelines

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   pytest
   black --check src/ tests/
   isort --check-only src/ tests/
   flake8 src/ tests/
   mypy src/aicodegen/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable names

### Commit Message Format

Use descriptive commit messages:

```
Type: Brief description

Longer description if needed
- Detail 1
- Detail 2

Closes #issue-number
```

Types:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Changes to existing features
- `Remove:` - Removing features
- `Docs:` - Documentation changes
- `Test:` - Adding or fixing tests

## Architecture Overview

### Project Structure

```
src/aicodegen/
├── core/           # Core functionality
│   ├── config.py   # Configuration management
│   └── generator.py # Main code generator
├── models/         # AI model implementations
│   ├── base.py     # Abstract base classes
│   └── openai_model.py # OpenAI integration
├── generators/     # Specific code generators
├── templates/      # Code templates
│   ├── python/     # Python templates
│   └── javascript/ # JavaScript templates
├── utils/          # Utility modules
│   ├── code_analyzer.py # Code analysis
│   └── file_handler.py  # File operations
└── cli.py          # Command-line interface
```

### Key Components

1. **CodeGenerator**: Main orchestrator class
2. **Config**: Configuration management with Pydantic
3. **BaseAIModel**: Abstract interface for AI models
4. **CodeAnalyzer**: Code analysis and metrics
5. **FileHandler**: File operations and project structure
6. **CLI**: Rich command-line interface

## Adding New Features

### Adding a New AI Provider

1. Create a new model class inheriting from `BaseAIModel`
2. Implement required methods: `generate_code`, `complete_code`, etc.
3. Update the generator to support the new provider
4. Add configuration options
5. Write tests

### Adding a New Language Support

1. Add language-specific templates
2. Update file extension mapping
3. Add language-specific analysis if needed
4. Update documentation

### Adding New CLI Commands

1. Add the command to `cli.py`
2. Implement the command logic
3. Add tests for the new command
4. Update help documentation

## Testing

### Test Structure

```
tests/
├── test_config.py     # Configuration tests
├── test_generator.py  # Generator tests
├── test_utils.py      # Utility tests
└── fixtures/          # Test data and fixtures
```

### Writing Tests

- Use pytest fixtures for common setup
- Mock external dependencies (OpenAI API)
- Test both success and error cases
- Aim for high test coverage

### Test Categories

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **CLI Tests**: Test command-line interface
4. **Mock Tests**: Test with mocked AI responses

## Documentation

### Code Documentation

- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings
- Keep documentation up to date

### User Documentation

- Update README.md for new features
- Add examples to the examples/ directory
- Update CLI help text

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release tag
4. GitHub Actions will handle the rest

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues and PRs

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow the project's coding standards

Thank you for contributing to AICodeGen!