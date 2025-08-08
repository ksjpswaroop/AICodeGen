"""Test code generator functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from aicodegen.core.generator import CodeGenerator
from aicodegen.core.config import Config


class TestCodeGenerator:
    """Test the main code generator functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = Config()
        config.ai_model.api_key = "test-key"
        return config
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_generator_initialization(self, config):
        """Test generator initialization."""
        with patch('aicodegen.models.openai_model.OpenAIModel'):
            generator = CodeGenerator(config)
            assert generator.config == config
            assert generator.ai_model is not None
    
    @patch('aicodegen.models.openai_model.OpenAIModel')
    def test_generate_code_basic(self, mock_model_class, config):
        """Test basic code generation."""
        # Mock the AI model
        mock_model = Mock()
        mock_model.generate_code.return_value = "print('Hello, World!')"
        mock_model_class.return_value = mock_model
        
        generator = CodeGenerator(config)
        result = generator.generate_code("Create a hello world program")
        
        assert result == "print('Hello, World!')"
        mock_model.generate_code.assert_called_once_with("Create a hello world program")
    
    @patch('aicodegen.models.openai_model.OpenAIModel')
    def test_generate_code_with_file_output(self, mock_model_class, config, temp_dir):
        """Test code generation with file output."""
        # Setup
        mock_model = Mock()
        mock_model.generate_code.return_value = "print('Hello, World!')"
        mock_model_class.return_value = mock_model
        
        config.code_gen.output_directory = str(temp_dir)
        generator = CodeGenerator(config)
        
        # Generate code with file output
        result = generator.generate_code(
            "Create a hello world program",
            output_file="hello.py"
        )
        
        # Verify
        assert result == "print('Hello, World!')"
        output_file = temp_dir / "hello.py"
        assert output_file.exists()
        assert output_file.read_text() == "print('Hello, World!')"
    
    @patch('aicodegen.models.openai_model.OpenAIModel')
    def test_generate_project(self, mock_model_class, config, temp_dir):
        """Test project generation."""
        # Setup
        mock_model = Mock()
        mock_model.generate_code.side_effect = [
            "# Main module",
            "# Utils module", 
            "# Test module",
            "# README content"
        ]
        mock_model_class.return_value = mock_model
        
        config.code_gen.output_directory = str(temp_dir)
        generator = CodeGenerator(config)
        
        # Generate project
        result = generator.generate_project(
            "A simple calculator app",
            "calculator",
            ["main", "utils", "tests", "readme"]
        )
        
        # Verify
        assert len(result) == 4
        assert "main.py" in result
        assert "utils.py" in result
        assert "tests.py" in result
        assert "README.md" in result
        
        # Check files were created
        project_dir = temp_dir / "calculator"
        assert project_dir.exists()
        assert (project_dir / "main.py").exists()
        assert (project_dir / "utils.py").exists()
        assert (project_dir / "tests.py").exists()
        assert (project_dir / "README.md").exists()
    
    def test_get_file_extension(self, config):
        """Test file extension determination."""
        with patch('aicodegen.models.openai_model.OpenAIModel'):
            generator = CodeGenerator(config)
            
            config.code_gen.language = "python"
            assert generator._get_file_extension() == "py"
            
            config.code_gen.language = "javascript"
            assert generator._get_file_extension() == "js"
            
            config.code_gen.language = "java"
            assert generator._get_file_extension() == "java"
            
            config.code_gen.language = "unknown"
            assert generator._get_file_extension() == "txt"