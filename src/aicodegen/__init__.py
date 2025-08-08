"""
AICodeGen - AI-Powered Software Engineering and Code Generation Platform

This package provides intelligent code generation capabilities using various AI models
and techniques to assist software developers in creating high-quality code efficiently.
"""

__version__ = "0.1.0"
__author__ = "AICodeGen Team"
__email__ = "team@aicodegen.dev"

from .core.generator import CodeGenerator
from .core.config import Config

__all__ = ["CodeGenerator", "Config"]