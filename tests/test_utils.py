"""Test utilities."""

import pytest
from pathlib import Path
import tempfile

from aicodegen.utils.code_analyzer import CodeAnalyzer
from aicodegen.utils.file_handler import FileHandler


class TestCodeAnalyzer:
    """Test code analysis functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a code analyzer instance."""
        return CodeAnalyzer()
    
    def test_analyze_python_code_basic(self, analyzer):
        """Test basic Python code analysis."""
        code = '''
def hello_world():
    """Print hello world."""
    print("Hello, World!")

class Calculator:
    """A simple calculator class."""
    
    def add(self, a, b):
        return a + b
'''
        
        result = analyzer.analyze_python_code(code)
        
        assert 'error' not in result
        assert result['lines_of_code'] == 10
        assert len(result['functions']) == 2  # hello_world and add
        assert len(result['classes']) == 1   # Calculator
        assert result['functions'][0]['name'] == 'hello_world'
        assert result['classes'][0]['name'] == 'Calculator'
    
    def test_analyze_python_code_syntax_error(self, analyzer):
        """Test analysis with syntax error."""
        code = '''
def broken_function(
    print("This has a syntax error")
'''
        
        result = analyzer.analyze_python_code(code)
        
        assert 'error' in result
        assert result['valid'] is False
    
    def test_count_lines(self, analyzer):
        """Test line counting functionality."""
        code = '''# This is a comment
def hello():
    """Docstring"""
    print("Hello")

# Another comment

def goodbye():
    print("Goodbye")
'''
        
        result = analyzer.count_lines(code)
        
        assert result['total'] == 9
        assert result['comment'] == 2
        assert result['blank'] == 2
        assert result['code'] == 5
    
    def test_validate_syntax_valid(self, analyzer):
        """Test syntax validation with valid code."""
        code = '''
def valid_function():
    return "This is valid Python"
'''
        
        result = analyzer.validate_syntax(code)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_syntax_invalid(self, analyzer):
        """Test syntax validation with invalid code."""
        code = '''
def invalid_function(
    return "Missing closing parenthesis"
'''
        
        result = analyzer.validate_syntax(code)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0


class TestFileHandler:
    """Test file handling functionality."""
    
    @pytest.fixture
    def file_handler(self):
        """Create a file handler instance."""
        return FileHandler()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_save_and_read_code(self, file_handler, temp_dir):
        """Test saving and reading code files."""
        code = "print('Hello, World!')"
        file_path = temp_dir / "test.py"
        
        # Save code
        file_handler.save_code(code, file_path)
        
        # Verify file exists
        assert file_path.exists()
        
        # Read code back
        read_code = file_handler.read_code(file_path)
        assert read_code == code
    
    def test_create_project_structure(self, file_handler, temp_dir):
        """Test project structure creation."""
        structure = {
            "src": {
                "main.py": "print('main')",
                "utils": {
                    "helper.py": "# helper functions"
                }
            },
            "tests": {
                "test_main.py": "# tests"
            },
            "README.md": "# Project README"
        }
        
        project_path = temp_dir / "test_project"
        file_handler.create_project_structure(project_path, structure)
        
        # Verify structure was created
        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "src" / "utils" / "helper.py").exists()
        assert (project_path / "tests" / "test_main.py").exists()
        assert (project_path / "README.md").exists()
        
        # Verify file contents
        assert (project_path / "src" / "main.py").read_text() == "print('main')"
        assert (project_path / "README.md").read_text() == "# Project README"
    
    def test_backup_file(self, file_handler, temp_dir):
        """Test file backup functionality."""
        # Create original file
        original_file = temp_dir / "original.py"
        original_content = "print('original')"
        file_handler.save_code(original_content, original_file)
        
        # Create backup
        backup_path = file_handler.backup_file(original_file)
        
        # Verify backup exists and has correct content
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
        assert backup_path.name == "original.py.bak"
    
    def test_get_file_info(self, file_handler, temp_dir):
        """Test file information retrieval."""
        file_path = temp_dir / "info_test.py"
        file_handler.save_code("test content", file_path)
        
        info = file_handler.get_file_info(file_path)
        
        assert info['exists'] is True
        assert info['name'] == "info_test.py"
        assert info['extension'] == ".py"
        assert info['size'] > 0
        assert 'created' in info
        assert 'modified' in info