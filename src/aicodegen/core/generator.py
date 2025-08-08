"""Core code generation functionality."""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import jinja2
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from ..models.base import BaseAIModel
from ..models.openai_model import OpenAIModel
from ..utils.file_handler import FileHandler


class CodeGenerator:
    """Main code generator class that orchestrates AI models and templates."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the code generator with configuration."""
        self.config = config or Config.from_env()
        self.console = Console()
        self.file_handler = FileHandler()
        self.ai_model = self._initialize_ai_model()
        self.template_env = self._initialize_template_environment()
        
        # Set up logging
        log_level = logging.DEBUG if self.config.debug else logging.INFO
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
    
    def _initialize_ai_model(self) -> BaseAIModel:
        """Initialize the AI model based on configuration."""
        if self.config.ai_model.provider == "openai":
            return OpenAIModel(self.config.ai_model)
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.ai_model.provider}")
    
    def _initialize_template_environment(self) -> jinja2.Environment:
        """Initialize Jinja2 template environment."""
        template_path = Path(self.config.code_gen.template_directory)
        if template_path.exists():
            loader = jinja2.FileSystemLoader(str(template_path))
        else:
            # Use built-in templates if custom directory doesn't exist
            package_templates = Path(__file__).parent.parent / "templates"
            loader = jinja2.FileSystemLoader(str(package_templates))
        
        return jinja2.Environment(
            loader=loader,
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate_code(
        self,
        prompt: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate code based on a prompt and optional template.
        
        Args:
            prompt: Natural language description of what to generate
            template_name: Optional template to use for structure
            context: Additional context variables for template rendering
            output_file: Optional file path to save the generated code
            
        Returns:
            Generated code as a string
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating code...", total=None)
            
            try:
                # Generate code using AI model
                progress.update(task, description="Calling AI model...")
                generated_code = self.ai_model.generate_code(prompt)
                
                # Apply template if specified
                if template_name:
                    progress.update(task, description="Applying template...")
                    generated_code = self._apply_template(
                        template_name, 
                        generated_code, 
                        context or {}
                    )
                
                # Save to file if specified
                if output_file:
                    progress.update(task, description="Saving to file...")
                    output_path = Path(self.config.code_gen.output_directory) / output_file
                    self.file_handler.save_code(generated_code, output_path)
                    self.console.print(f"✅ Code saved to: {output_path}")
                
                progress.update(task, description="✅ Code generation complete!")
                return generated_code
                
            except Exception as e:
                self.logger.error(f"Error generating code: {e}")
                self.console.print(f"❌ Error: {e}")
                raise
    
    def _apply_template(
        self, 
        template_name: str, 
        code: str, 
        context: Dict[str, Any]
    ) -> str:
        """Apply a template to generated code."""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(generated_code=code, **context)
        except jinja2.TemplateNotFound:
            self.logger.warning(f"Template {template_name} not found, using raw code")
            return code
    
    def generate_project(
        self,
        project_description: str,
        project_name: str,
        components: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a complete project structure based on description.
        
        Args:
            project_description: High-level description of the project
            project_name: Name for the project
            components: List of specific components to generate
            
        Returns:
            Dictionary mapping file paths to generated content
        """
        self.console.print(f"🚀 Generating project: {project_name}")
        
        project_files = {}
        components = components or ["main", "utils", "tests", "readme"]
        
        for component in components:
            component_prompt = f"""
            Generate {component} component for a project called '{project_name}'.
            Project description: {project_description}
            Target language: {self.config.code_gen.language}
            """
            
            self.console.print(f"📝 Generating {component}...")
            code = self.generate_code(component_prompt)
            
            # Determine file extension based on language
            ext = self._get_file_extension()
            filename = f"{component}.{ext}" if component != "readme" else "README.md"
            project_files[filename] = code
        
        # Save all files
        project_dir = Path(self.config.code_gen.output_directory) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in project_files.items():
            file_path = project_dir / filename
            self.file_handler.save_code(content, file_path)
        
        self.console.print(f"✅ Project generated in: {project_dir}")
        return project_files
    
    def _get_file_extension(self) -> str:
        """Get file extension based on configured language."""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "csharp": "cs",
            "go": "go",
            "rust": "rs"
        }
        return extensions.get(self.config.code_gen.language, "txt")