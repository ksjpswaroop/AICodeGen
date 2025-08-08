# AICodeGen

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AICodeGen** is an intelligent code generation platform that leverages advanced AI models to automatically generate high-quality code based on natural language descriptions, specifications, or existing code patterns.

## 🚀 Features

- **Natural Language to Code**: Generate code from plain English descriptions
- **Multi-Language Support**: Supports Python, JavaScript, Java, C++, and more
- **Code Completion**: Intelligent code completion and suggestions
- **Code Refactoring**: Automated code optimization and refactoring
- **Documentation Generation**: Automatic generation of code documentation
- **Test Generation**: Create unit tests based on code functionality
- **API Integration**: RESTful API for seamless integration

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Install from PyPI

```bash
pip install aicodegen
```

### Install from Source

```bash
git clone https://github.com/ksjpswaroop/AICodeGen.git
cd AICodeGen
pip install -e .
```

### Docker Installation

```bash
docker pull aicodegen/latest
docker run -p 8000:8000 aicodegen/latest
```

## ⚡ Quick Start

### Command Line Interface

```bash
# Generate a Python function
aicodegen generate --lang python --description "Create a function that calculates fibonacci numbers"

# Generate from a specification file
aicodegen generate --spec requirements.txt --output src/

# Start interactive mode
aicodegen interactive
```

### Python API

```python
from aicodegen import CodeGenerator

# Initialize the generator
generator = CodeGenerator(model="gpt-4", language="python")

# Generate code from description
code = generator.generate(
    description="Create a class for managing user authentication",
    style="object-oriented"
)

print(code)
```

## 📖 Usage

### Basic Code Generation

Generate code by providing a natural language description:

```python
from aicodegen import CodeGenerator

generator = CodeGenerator()

# Generate a sorting algorithm
code = generator.generate(
    description="Implement quicksort algorithm with comments",
    language="python",
    include_tests=True
)
```

### Advanced Features

#### Code Completion

```python
# Complete partial code
partial_code = "def calculate_compound_interest(principal, rate"
completed = generator.complete(partial_code)
```

#### Code Refactoring

```python
# Refactor existing code
original_code = "..."
refactored = generator.refactor(
    code=original_code,
    improvements=["performance", "readability"]
)
```

#### Documentation Generation

```python
# Generate documentation for existing code
docs = generator.generate_docs(
    code="def fibonacci(n): ...",
    format="sphinx"
)
```

## 🔌 API Documentation

### REST API Endpoints

#### Generate Code

```http
POST /api/v1/generate
Content-Type: application/json

{
    "description": "Create a REST API endpoint for user registration",
    "language": "python",
    "framework": "flask",
    "include_tests": true
}
```

#### Code Completion

```http
POST /api/v1/complete
Content-Type: application/json

{
    "code": "def process_data(data):",
    "language": "python",
    "max_lines": 10
}
```

#### Health Check

```http
GET /api/v1/health
```

### Response Format

```json
{
    "status": "success",
    "data": {
        "generated_code": "...",
        "language": "python",
        "timestamp": "2024-01-01T00:00:00Z"
    },
    "metadata": {
        "model_used": "gpt-4",
        "tokens_used": 150,
        "execution_time": "2.3s"
    }
}
```

## 📚 Examples

### Example 1: Web API Generation

```python
from aicodegen import CodeGenerator

generator = CodeGenerator(language="python")

api_code = generator.generate(
    description="""
    Create a FastAPI application with the following endpoints:
    - GET /users - List all users
    - POST /users - Create a new user
    - GET /users/{id} - Get user by ID
    - PUT /users/{id} - Update user
    - DELETE /users/{id} - Delete user
    Include Pydantic models and basic validation.
    """,
    framework="fastapi"
)

print(api_code)
```

### Example 2: Data Processing Pipeline

```python
pipeline_code = generator.generate(
    description="""
    Create a data processing pipeline that:
    1. Reads CSV files from a directory
    2. Cleans the data (removes nulls, duplicates)
    3. Applies transformations (normalize, scale)
    4. Saves results to a database
    Use pandas and sqlalchemy.
    """,
    language="python",
    libraries=["pandas", "sqlalchemy"]
)
```

### Example 3: Machine Learning Model

```python
ml_code = generator.generate(
    description="""
    Create a machine learning model for binary classification:
    - Load and preprocess data
    - Train a Random Forest classifier
    - Evaluate with cross-validation
    - Save the trained model
    Include proper error handling and logging.
    """,
    domain="machine-learning",
    libraries=["scikit-learn", "pandas", "joblib"]
)
```

## ⚙️ Configuration

### Configuration File

Create a `aicodegen.yaml` file in your project root:

```yaml
model:
  name: "gpt-4"
  temperature: 0.7
  max_tokens: 2048

output:
  format: "formatted"
  include_comments: true
  include_docstrings: true

languages:
  default: "python"
  supported: ["python", "javascript", "java", "cpp", "go"]

api:
  host: "localhost"
  port: 8000
  rate_limit: 100

logging:
  level: "INFO"
  file: "aicodegen.log"
```

### Environment Variables

```bash
export AICODEGEN_API_KEY="your-api-key"
export AICODEGEN_MODEL="gpt-4"
export AICODEGEN_LOG_LEVEL="DEBUG"
```

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/ksjpswaroop/AICodeGen.git
cd AICodeGen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aicodegen

# Run specific test file
pytest tests/test_generator.py
```

### Code Quality

```bash
# Format code
black aicodegen/
isort aicodegen/

# Lint code
flake8 aicodegen/
pylint aicodegen/

# Type checking
mypy aicodegen/
```

### Building Documentation

```bash
cd docs/
make html
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow our coding standards
4. **Add tests**: Ensure your changes are tested
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Contribution Guidelines

- Write clear, readable code with proper documentation
- Add tests for any new functionality
- Follow the existing code style and conventions
- Update documentation for any API changes
- Ensure all tests pass before submitting

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://aicodegen.readthedocs.io](https://aicodegen.readthedocs.io)
- **PyPI Package**: [https://pypi.org/project/aicodegen/](https://pypi.org/project/aicodegen/)
- **Issues**: [https://github.com/ksjpswaroop/AICodeGen/issues](https://github.com/ksjpswaroop/AICodeGen/issues)
- **Discussions**: [https://github.com/ksjpswaroop/AICodeGen/discussions](https://github.com/ksjpswaroop/AICodeGen/discussions)

## 🙋‍♂️ Support

- **Documentation**: Check our comprehensive [documentation](https://aicodegen.readthedocs.io)
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/ksjpswaroop/AICodeGen/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/ksjpswaroop/AICodeGen/discussions)
- **Email**: Contact us at support@aicodegen.dev

---

**Made with ❤️ by the AICodeGen Team**