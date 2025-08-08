"""File handling utilities."""

import os
from pathlib import Path
from typing import Optional
import logging


class FileHandler:
    """Utility class for handling file operations in code generation."""
    
    def __init__(self):
        """Initialize file handler."""
        self.logger = logging.getLogger(__name__)
    
    def save_code(self, code: str, file_path: Path) -> None:
        """
        Save generated code to a file.
        
        Args:
            code: Code content to save
            file_path: Path where to save the file
        """
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write code to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.logger.info(f"Code saved to: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving code to {file_path}: {e}")
            raise
    
    def read_code(self, file_path: Path) -> str:
        """
        Read code from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Content of the file as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading code from {file_path}: {e}")
            raise
    
    def create_project_structure(self, project_path: Path, structure: dict) -> None:
        """
        Create a project directory structure.
        
        Args:
            project_path: Root path for the project
            structure: Dictionary defining the directory structure
        """
        try:
            for item, content in structure.items():
                item_path = project_path / item
                
                if isinstance(content, dict):
                    # It's a directory
                    item_path.mkdir(parents=True, exist_ok=True)
                    if content:  # Has subdirectories/files
                        self.create_project_structure(item_path, content)
                else:
                    # It's a file
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(content if content else "")
            
            self.logger.info(f"Project structure created at: {project_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating project structure: {e}")
            raise
    
    def backup_file(self, file_path: Path) -> Path:
        """
        Create a backup of an existing file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
        counter = 1
        
        # Find a unique backup filename
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.bak{counter}")
            counter += 1
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": file_path.suffix,
                "name": file_path.name,
                "exists": file_path.exists()
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return {"exists": False, "error": str(e)}