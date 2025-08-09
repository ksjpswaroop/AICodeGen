"""Configuration management for AICodeGen."""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AIModelConfig(BaseModel):
    """Configuration for AI model settings."""
    
    provider: str = Field(default="openai", description="AI provider (openai, huggingface, etc.)")
    model_name: str = Field(default="gpt-3.5-turbo", description="Model name to use")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    max_tokens: int = Field(default=1000, description="Maximum tokens in response")
    temperature: float = Field(default=0.7, description="Model temperature for creativity")


class CodeGenConfig(BaseModel):
    """Configuration for code generation settings."""
    
    output_directory: str = Field(default="./generated", description="Output directory for generated code")
    template_directory: str = Field(default="./templates", description="Directory containing code templates")
    language: str = Field(default="python", description="Target programming language")
    style_guide: str = Field(default="pep8", description="Code style guide to follow")


class Config(BaseModel):
    """Main configuration class for AICodeGen."""
    
    ai_model: AIModelConfig = Field(default_factory=AIModelConfig)
    code_gen: CodeGenConfig = Field(default_factory=CodeGenConfig)
    debug: bool = Field(default=False, description="Enable debug mode")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config_data = {}
        
        # AI Model configuration from environment
        if os.getenv("AICODEGEN_PROVIDER"):
            config_data.setdefault("ai_model", {})["provider"] = os.getenv("AICODEGEN_PROVIDER")
        if os.getenv("AICODEGEN_MODEL"):
            config_data.setdefault("ai_model", {})["model_name"] = os.getenv("AICODEGEN_MODEL")
        if os.getenv("OPENAI_API_KEY"):
            config_data.setdefault("ai_model", {})["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("AICODEGEN_MAX_TOKENS"):
            config_data.setdefault("ai_model", {})["max_tokens"] = int(os.getenv("AICODEGEN_MAX_TOKENS"))
        
        # Code generation configuration from environment
        if os.getenv("AICODEGEN_OUTPUT_DIR"):
            config_data.setdefault("code_gen", {})["output_directory"] = os.getenv("AICODEGEN_OUTPUT_DIR")
        if os.getenv("AICODEGEN_LANGUAGE"):
            config_data.setdefault("code_gen", {})["language"] = os.getenv("AICODEGEN_LANGUAGE")
        
        # Debug mode
        if os.getenv("AICODEGEN_DEBUG"):
            config_data["debug"] = os.getenv("AICODEGEN_DEBUG").lower() == "true"
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()