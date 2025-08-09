#!/usr/bin/env python3
"""
AICodeGen Demo Script

This script demonstrates the capabilities of AICodeGen without requiring an API key.
It showcases the core functionality that would work when connected to OpenAI.
"""

from aicodegen import CodeGenerator, Config
from aicodegen.utils.code_analyzer import CodeAnalyzer
from aicodegen.utils.file_handler import FileHandler
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import tempfile
from pathlib import Path

console = Console()

def demo_configuration():
    """Demonstrate configuration system."""
    console.print(Panel("🔧 Configuration System Demo", style="bold blue"))
    
    config = Config.from_env()
    console.print("Default Configuration:")
    console.print(f"Provider: {config.ai_model.provider}")
    console.print(f"Model: {config.ai_model.model_name}")
    console.print(f"Language: {config.code_gen.language}")
    console.print(f"Output Dir: {config.code_gen.output_directory}")
    console.print()

def demo_code_analysis():
    """Demonstrate code analysis capabilities."""
    console.print(Panel("📊 Code Analysis Demo", style="bold green"))
    
    analyzer = CodeAnalyzer()
    
    # Sample Python code
    sample_code = '''
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def is_prime(num):
        """Check if a number is prime."""
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
    
    def fibonacci_sequence(self, length):
        """Generate Fibonacci sequence."""
        if length <= 0:
            return []
        elif length == 1:
            return [0]
        elif length == 2:
            return [0, 1]
        
        sequence = [0, 1]
        for i in range(2, length):
            sequence.append(sequence[i-1] + sequence[i-2])
        return sequence
'''
    
    analysis = analyzer.analyze_python_code(sample_code)
    
    console.print("Analysis Results:")
    console.print(f"• Lines of code: {analysis['lines_of_code']}")
    console.print(f"• Functions: {len(analysis['functions'])}")
    console.print(f"• Classes: {len(analysis['classes'])}")
    console.print(f"• Complexity: {analysis['complexity']}")
    
    console.print("\nFunctions found:")
    for func in analysis['functions']:
        console.print(f"  - {func['name']}() at line {func['line']}")
    
    console.print("\nClasses found:")
    for cls in analysis['classes']:
        console.print(f"  - {cls['name']} at line {cls['line']}")
    
    console.print()

def demo_file_operations():
    """Demonstrate file handling capabilities."""
    console.print(Panel("📁 File Operations Demo", style="bold yellow"))
    
    file_handler = FileHandler()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Demo project structure creation
        project_structure = {
            "src": {
                "main.py": "print('Hello from main!')",
                "utils": {
                    "helpers.py": "# Helper functions",
                    "__init__.py": ""
                }
            },
            "tests": {
                "test_main.py": "# Test cases",
                "__init__.py": ""
            },
            "README.md": "# Demo Project\n\nThis is a demo project structure.",
            "requirements.txt": "requests>=2.25.0\nnumpy>=1.20.0"
        }
        
        project_path = temp_path / "demo_project"
        file_handler.create_project_structure(project_path, project_structure)
        
        console.print("Created project structure:")
        for root, dirs, files in project_path.walk():
            level = len(root.relative_to(project_path).parts)
            indent = "  " * level
            console.print(f"{indent}{root.name}/")
            subindent = "  " * (level + 1)
            for file in files:
                console.print(f"{subindent}{file}")
        
        # Demo file info
        readme_path = project_path / "README.md"
        file_info = file_handler.get_file_info(readme_path)
        console.print(f"\nREADME.md info:")
        console.print(f"  Size: {file_info['size']} bytes")
        console.print(f"  Extension: {file_info['extension']}")
        console.print(f"  Exists: {file_info['exists']}")
    
    console.print()

def demo_templates():
    """Demonstrate template system."""
    console.print(Panel("📋 Template System Demo", style="bold magenta"))
    
    # Show available templates
    templates_path = Path("src/aicodegen/templates")
    if templates_path.exists():
        console.print("Available templates:")
        for template_file in templates_path.rglob("*.py"):
            relative_path = template_file.relative_to(templates_path)
            console.print(f"  - {relative_path}")
        
        # Show a template content
        python_class_template = templates_path / "python" / "class.py"
        if python_class_template.exists():
            console.print("\nPython class template preview:")
            template_content = python_class_template.read_text()
            syntax = Syntax(template_content[:300] + "...", "python", theme="monokai")
            console.print(syntax)
    
    console.print()

def demo_cli_commands():
    """Show available CLI commands."""
    console.print(Panel("💻 CLI Commands Available", style="bold cyan"))
    
    commands = [
        ("aicodegen generate", "Generate code from natural language prompts"),
        ("aicodegen project", "Generate complete project structures"),
        ("aicodegen analyze", "Analyze code complexity and structure"),
        ("aicodegen explain", "Get AI explanations of existing code"),
        ("aicodegen review", "AI-powered code reviews"),
        ("aicodegen config-show", "Display current configuration")
    ]
    
    console.print("Available commands:")
    for cmd, desc in commands:
        console.print(f"  • [bold]{cmd}[/bold]")
        console.print(f"    {desc}")
        console.print()

def main():
    """Run the complete demo."""
    console.print(Panel.fit(
        "🚀 AICodeGen - AI-Powered Software Engineering Platform Demo", 
        style="bold white on blue"
    ))
    console.print()
    
    demo_configuration()
    demo_code_analysis()
    demo_file_operations()
    demo_templates()
    demo_cli_commands()
    
    console.print(Panel(
        "✨ Demo Complete!\n\n"
        "To use AICodeGen with AI features:\n"
        "1. Set your OPENAI_API_KEY environment variable\n"
        "2. Run: aicodegen generate 'your prompt here'\n"
        "3. Explore the CLI commands shown above",
        style="bold green"
    ))

if __name__ == "__main__":
    main()