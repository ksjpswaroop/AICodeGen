<general_rules>
- Always follow Python PEP 8 style guidelines for code formatting and naming conventions
- Before creating new AI model classes or utilities, search the `aicodegen/models/` and `aicodegen/utils/` directories to avoid duplication
- When adding new code generation templates, place them in the `templates/` directory organized by programming language or framework
- Use type hints for all function parameters and return values to improve code clarity and IDE support
- All new modules should include comprehensive docstrings following Google or NumPy docstring format
- Before implementing new functionality, check if similar capabilities exist in the `aicodegen/core/` module
- Run code formatting with `black .` and linting with `flake8` before committing changes
- Use meaningful commit messages that clearly describe the changes made
- When working with AI models, always include error handling for API failures and rate limiting
- Configuration should be managed through environment variables or config files in the `config/` directory
</general_rules>

<repository_structure>
This repository follows a modular Python package structure for an AI-powered code generation tool:

- `aicodegen/` - Main Python package containing core functionality
  - `core/` - Core code generation engine and orchestration logic
  - `models/` - AI model integrations and wrappers (OpenAI, Anthropic, etc.)
  - `generators/` - Language-specific code generators and parsers
  - `utils/` - Shared utilities for file handling, text processing, and validation
- `templates/` - Code generation templates organized by language/framework
- `config/` - Configuration files and environment-specific settings
- `tests/` - Test suite with unit and integration tests
- `examples/` - Example usage scripts and demonstrations
- `docs/` - Documentation and API references
- `scripts/` - Development and deployment scripts

The project is designed to be extensible, allowing easy addition of new AI models, programming languages, and generation templates.
</repository_structure>

<dependencies_and_installation>
This project uses Python 3.8+ and follows modern Python packaging standards:

- Dependencies are managed through `pyproject.toml` for package metadata and core dependencies
- Development dependencies are specified in `requirements-dev.txt`
- Install the package in development mode: `pip install -e .`
- Install development dependencies: `pip install -r requirements-dev.txt`
- Use virtual environments (venv or conda) to isolate project dependencies
- Pin major versions for AI API libraries (openai, anthropic) to ensure compatibility
- Environment variables for API keys should be managed through `.env` files (not committed to git)
- For production deployments, use `pip install aicodegen` once published to PyPI
</dependencies_and_installation>

<testing_instructions>
The project uses pytest as the primary testing framework:

- Run all tests: `pytest`
- Run tests with coverage: `pytest --cov=aicodegen`
- Run specific test categories: `pytest tests/unit/` or `pytest tests/integration/`
- Test files should mirror the source code structure in the `tests/` directory
- Unit tests should focus on individual functions and classes without external API calls
- Integration tests should test end-to-end workflows but use mocked AI API responses
- All AI model interactions should be mocked in tests to avoid API costs and ensure reliability
- Test data and fixtures should be placed in `tests/fixtures/`
- Aim for >80% code coverage on core functionality
- Use parametrized tests for testing multiple programming languages or templates
</testing_instructions>

<pull_request_formatting>
</pull_request_formatting>
