"""Test configuration module."""

import pytest
import os
from unittest.mock import patch

from aicodegen.core.config import Config, AIModelConfig, CodeGenConfig


class TestConfig:
    """Test the configuration system."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.ai_model.provider == "openai"
        assert config.ai_model.model_name == "gpt-3.5-turbo"
        assert config.ai_model.max_tokens == 1000
        assert config.ai_model.temperature == 0.7
        assert config.code_gen.output_directory == "./generated"
        assert config.code_gen.language == "python"
        assert config.debug is False
    
    def test_ai_model_config(self):
        """Test AI model configuration."""
        config = AIModelConfig(
            provider="openai",
            model_name="gpt-4",
            max_tokens=2000,
            temperature=0.5
        )
        
        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
    
    def test_code_gen_config(self):
        """Test code generation configuration."""
        config = CodeGenConfig(
            output_directory="./output",
            language="javascript",
            style_guide="standard"
        )
        
        assert config.output_directory == "./output"
        assert config.language == "javascript"
        assert config.style_guide == "standard"
    
    @patch.dict(os.environ, {
        'AICODEGEN_PROVIDER': 'openai',
        'AICODEGEN_MODEL': 'gpt-4',
        'OPENAI_API_KEY': 'test-key',
        'AICODEGEN_MAX_TOKENS': '1500',
        'AICODEGEN_OUTPUT_DIR': './test-output',
        'AICODEGEN_LANGUAGE': 'python',
        'AICODEGEN_DEBUG': 'true'
    })
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        config = Config.from_env()
        
        assert config.ai_model.provider == "openai"
        assert config.ai_model.model_name == "gpt-4"
        assert config.ai_model.api_key == "test-key"
        assert config.ai_model.max_tokens == 1500
        assert config.code_gen.output_directory == "./test-output"
        assert config.code_gen.language == "python"
        assert config.debug is True
    
    def test_config_to_dict(self):
        """Test configuration serialization to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "ai_model" in config_dict
        assert "code_gen" in config_dict
        assert "debug" in config_dict
        assert config_dict["ai_model"]["provider"] == "openai"