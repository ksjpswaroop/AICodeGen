"""OpenAI model implementation."""

import openai
from typing import Dict, Any, List, Optional
import logging

from .base import BaseAIModel
from ..core.config import AIModelConfig


class OpenAIModel(BaseAIModel):
    """OpenAI GPT model implementation for code generation."""
    
    def __init__(self, config: AIModelConfig):
        """Initialize OpenAI model with configuration."""
        super().__init__(config.model_dump())
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        if config.api_key:
            openai.api_key = config.api_key
        else:
            self.logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=config.api_key)
    
    def _make_request(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """Make a request to OpenAI API."""
        try:
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=full_messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error making OpenAI request: {e}")
            raise
    
    def generate_code(self, prompt: str) -> str:
        """Generate code based on a natural language prompt."""
        system_prompt = """You are an expert software developer. Generate clean, 
        well-documented, and efficient code based on the user's requirements. 
        Follow best practices and include appropriate comments."""
        
        messages = [{
            "role": "user",
            "content": f"Generate code for the following requirement: {prompt}"
        }]
        
        return self._make_request(messages, system_prompt)
    
    def complete_code(self, partial_code: str, context: str = "") -> str:
        """Complete partial code given context."""
        system_prompt = """You are an expert software developer. Complete the given 
        partial code following the established patterns and best practices. 
        Ensure the completion is syntactically correct and logically sound."""
        
        user_content = f"Complete this code:\n\n{partial_code}"
        if context:
            user_content += f"\n\nContext: {context}"
        
        messages = [{"role": "user", "content": user_content}]
        
        return self._make_request(messages, system_prompt)
    
    def explain_code(self, code: str) -> str:
        """Generate explanation for given code."""
        system_prompt = """You are an expert software developer and technical writer. 
        Explain the given code in clear, understandable language. Break down complex 
        concepts and describe what each part does."""
        
        messages = [{
            "role": "user",
            "content": f"Explain this code:\n\n{code}"
        }]
        
        return self._make_request(messages, system_prompt)
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code and provide suggestions."""
        system_prompt = """You are an expert code reviewer. Review the given code 
        and provide constructive feedback including:
        1. Code quality issues
        2. Performance improvements
        3. Security concerns
        4. Best practice violations
        5. Suggestions for improvement
        
        Format your response as a structured review."""
        
        messages = [{
            "role": "user",
            "content": f"Review this code:\n\n{code}"
        }]
        
        review_text = self._make_request(messages, system_prompt)
        
        # Parse the review into a structured format
        return {
            "overall_rating": "Good",  # This could be extracted from the response
            "suggestions": review_text,
            "issues_found": [],  # Could parse specific issues
            "improvements": []   # Could parse specific improvements
        }
    
    def generate_tests(self, code: str, test_framework: str = "pytest") -> str:
        """Generate unit tests for given code."""
        system_prompt = f"""You are an expert in test-driven development. 
        Generate comprehensive unit tests for the given code using {test_framework}. 
        Include edge cases, error conditions, and ensure good test coverage."""
        
        messages = [{
            "role": "user",
            "content": f"Generate {test_framework} tests for this code:\n\n{code}"
        }]
        
        return self._make_request(messages, system_prompt)
    
    def refactor_code(self, code: str, refactoring_goal: str) -> str:
        """Refactor code according to specified goal."""
        system_prompt = """You are an expert in code refactoring. Refactor the given 
        code according to the specified goal while maintaining functionality. 
        Ensure the refactored code is clean, efficient, and follows best practices."""
        
        messages = [{
            "role": "user",
            "content": f"Refactor this code with goal: {refactoring_goal}\n\nCode:\n{code}"
        }]
        
        return self._make_request(messages, system_prompt)