"""Basic usage examples for AICodeGen."""

from aicodegen import CodeGenerator, Config

def basic_code_generation():
    """Demonstrate basic code generation."""
    print("=== Basic Code Generation ===")
    
    # Initialize generator with default configuration
    generator = CodeGenerator()
    
    # Generate a simple function
    prompt = "Create a Python function that calculates the factorial of a number"
    code = generator.generate_code(prompt)
    
    print("Generated code:")
    print(code)
    print()


def custom_configuration():
    """Demonstrate custom configuration."""
    print("=== Custom Configuration ===")
    
    # Create custom configuration
    config = Config()
    config.ai_model.model_name = "gpt-4"
    config.ai_model.temperature = 0.5
    config.code_gen.language = "python"
    config.code_gen.style_guide = "pep8"
    
    generator = CodeGenerator(config)
    
    # Generate code with custom config
    prompt = "Create a class for managing a simple inventory system"
    code = generator.generate_code(prompt)
    
    print("Generated code with custom config:")
    print(code)
    print()


def project_generation():
    """Demonstrate project generation."""
    print("=== Project Generation ===")
    
    generator = CodeGenerator()
    
    # Generate a complete project
    project_files = generator.generate_project(
        project_description="A simple calculator application with basic arithmetic operations",
        project_name="calculator",
        components=["main", "calculator", "utils", "tests"]
    )
    
    print("Generated project files:")
    for filename, content in project_files.items():
        print(f"\n--- {filename} ---")
        print(content[:200] + "..." if len(content) > 200 else content)


def code_analysis():
    """Demonstrate code analysis capabilities."""
    print("=== Code Analysis ===")
    
    generator = CodeGenerator()
    
    # Sample code to analyze
    sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """A simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
    
    # Get explanation
    explanation = generator.ai_model.explain_code(sample_code)
    print("Code explanation:")
    print(explanation)
    print()
    
    # Get code review
    review = generator.ai_model.review_code(sample_code)
    print("Code review:")
    print(review['suggestions'])


def main():
    """Run all examples."""
    try:
        basic_code_generation()
        custom_configuration()
        project_generation()
        code_analysis()
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()