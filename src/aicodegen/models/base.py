"""Base AI model interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAIModel(ABC):
    """Abstract base class for AI models used in code generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the AI model with configuration."""
        self.config = config
    
    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        """
        Generate code based on a natural language prompt.
        
        Args:
            prompt: Natural language description of what to generate
            
        Returns:
            Generated code as a string
        """
        pass
    
    @abstractmethod
    def complete_code(self, partial_code: str, context: str = "") -> str:
        """
        Complete partial code given context.
        
        Args:
            partial_code: Incomplete code to complete
            context: Additional context for completion
            
        Returns:
            Completed code as a string
        """
        pass
    
    @abstractmethod
    def explain_code(self, code: str) -> str:
        """
        Generate explanation for given code.
        
        Args:
            code: Code to explain
            
        Returns:
            Natural language explanation of the code
        """
        pass
    
    @abstractmethod
    def review_code(self, code: str) -> Dict[str, Any]:
        """
        Review code and provide suggestions.
        
        Args:
            code: Code to review
            
        Returns:
            Dictionary containing review results and suggestions
        """
        pass