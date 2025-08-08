# AICodeGen

AI-Powered Software Engineering and Code Generation Platform

## Overview

AICodeGen is a comprehensive platform that leverages artificial intelligence to assist software developers in generating high-quality code efficiently. It provides intelligent code generation capabilities using various AI models and techniques, helping developers accelerate their workflow and improve code quality.

## Features

- **AI-Powered Code Generation**: Generate code from natural language descriptions
- **Multi-Language Support**: Support for Python, JavaScript, Java, C++, and more
- **Project Scaffolding**: Generate complete project structures
- **Code Analysis**: Analyze code complexity, structure, and quality
- **Code Review**: AI-powered code review and suggestions
- **Template System**: Customizable code templates
- **CLI Interface**: Easy-to-use command-line interface
- **Extensible Architecture**: Plugin-based system for custom generators

## Installation

```bash
# Clone the repository
git clone https://github.com/ksjpswaroop/AICodeGen.git
cd AICodeGen

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### 1. Set up your environment

```bash
export OPENAI_API_KEY="your-openai-api-key"
export AICODEGEN_LANGUAGE="python"
```

### 2. Generate code from a prompt

```bash
aicodegen generate "Create a function that calculates fibonacci numbers"
```

### 3. Generate a complete project

```bash
aicodegen project "A REST API for a todo app" todo-api
```

### 4. Analyze existing code

```bash
aicodegen analyze src/main.py
```

## Usage

### Command Line Interface

The `aicodegen` command provides several subcommands:

#### Generate Code
```bash
# Basic code generation
aicodegen generate "Create a class for handling user authentication"

# With output file
aicodegen generate "Create a calculator class" --output calculator.py

# Using a template
aicodegen generate "Create a web server" --template python/flask_app.py

# Specify language
aicodegen generate "Create a sorting algorithm" --language javascript
```

#### Generate Projects
```bash
# Generate a complete project
aicodegen project "A machine learning pipeline" ml-pipeline

# With specific components
aicodegen project "A web app" webapp --components main utils tests docs

# Custom output directory
aicodegen project "A CLI tool" cli-tool --output-dir ./projects
```

#### Code Analysis
```bash
# Analyze code structure
aicodegen analyze src/main.py

# Get AI explanation
aicodegen explain src/complex_algorithm.py

# AI code review
aicodegen review src/module.py
```

#### Configuration
```bash
# Show current configuration
aicodegen config-show
```

### Python API

```python
from aicodegen import CodeGenerator, Config

# Initialize with default config
generator = CodeGenerator()

# Generate code
code = generator.generate_code("Create a function to validate email addresses")
print(code)

# Generate a project
project_files = generator.generate_project(
    "A simple web scraper",
    "web-scraper",
    components=["main", "utils", "tests"]
)

# Custom configuration
config = Config()
config.ai_model.model_name = "gpt-4"
config.code_gen.language = "python"

generator = CodeGenerator(config)
```

## Configuration

AICodeGen can be configured through environment variables or configuration files:

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `AICODEGEN_PROVIDER`: AI provider (default: "openai")
- `AICODEGEN_MODEL`: Model name (default: "gpt-3.5-turbo")
- `AICODEGEN_MAX_TOKENS`: Maximum tokens (default: 1000)
- `AICODEGEN_OUTPUT_DIR`: Output directory (default: "./generated")
- `AICODEGEN_LANGUAGE`: Target language (default: "python")
- `AICODEGEN_DEBUG`: Enable debug mode (default: false)

### Configuration File

Create a `config.yaml` file:

```yaml
ai_model:
  provider: "openai"
  model_name: "gpt-4"
  max_tokens: 2000
  temperature: 0.7

code_gen:
  output_directory: "./output"
  language: "python"
  style_guide: "pep8"

debug: false
```

Use with: `aicodegen --config config.yaml generate "your prompt"`

## Templates

AICodeGen supports customizable templates for different code patterns:

### Built-in Templates

- `python/class.py`: Python class template
- `python/module.py`: Python module template
- `javascript/class.js`: JavaScript class template

### Custom Templates

Create your own templates using Jinja2 syntax:

```python
# templates/my_template.py
"""{{ description }}"""

class {{ class_name }}:
    def __init__(self):
        {{ generated_code | indent(8) }}
```

## Examples

See the `examples/` directory for sample projects and usage patterns:

- `examples/basic_usage.py`: Basic API usage
- `examples/custom_templates/`: Custom template examples
- `examples/project_generation/`: Project generation examples

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Project Structure

```
src/aicodegen/
├── core/           # Core functionality
├── models/         # AI model implementations
├── generators/     # Code generators
├── templates/      # Code templates
├── utils/          # Utility modules
└── cli.py          # Command-line interface

tests/              # Test suite
docs/               # Documentation
examples/           # Usage examples
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/ksjpswaroop/AICodeGen/docs)
- [Issues](https://github.com/ksjpswaroop/AICodeGen/issues)
- [Discussions](https://github.com/ksjpswaroop/AICodeGen/discussions)

## Roadmap

- [ ] Support for more AI providers (Anthropic, Cohere, etc.)
- [ ] Advanced code refactoring capabilities
- [ ] Integration with popular IDEs
- [ ] Code quality metrics and recommendations
- [ ] Collaborative code generation features
- [ ] Custom model fine-tuning support