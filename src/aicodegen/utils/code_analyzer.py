"""Code analysis utilities."""

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class CodeAnalyzer:
    """Utility class for analyzing code structure and complexity."""
    
    def __init__(self):
        """Initialize code analyzer."""
        pass
    
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code structure.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity": 0,
                "lines_of_code": len(code.splitlines()),
                "docstrings": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")
            
            # Calculate cyclomatic complexity (simplified)
            analysis["complexity"] = self._calculate_complexity(tree)
            
            return analysis
            
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}", "valid": False}
        except Exception as e:
            return {"error": f"Analysis error: {e}", "valid": False}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of AST."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With,
                               ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def extract_functions(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """
        Extract function definitions from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of function information dictionaries
        """
        if language.lower() == "python":
            return self._extract_python_functions(code)
        else:
            return self._extract_functions_regex(code, language)
    
    def _extract_python_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract Python functions using AST."""
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "returns": ast.unparse(node.returns) if node.returns else None,
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    })
            
            return functions
        except:
            return []
    
    def _extract_functions_regex(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract functions using regex patterns for various languages."""
        patterns = {
            "javascript": r"function\s+(\w+)\s*\([^)]*\)",
            "java": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)",
            "cpp": r"(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{",
            "csharp": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)"
        }
        
        pattern = patterns.get(language.lower())
        if not pattern:
            return []
        
        functions = []
        for i, line in enumerate(code.splitlines(), 1):
            match = re.search(pattern, line)
            if match:
                functions.append({
                    "name": match.group(1),
                    "line": i,
                    "signature": line.strip()
                })
        
        return functions
    
    def validate_syntax(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code syntax.
        
        Args:
            code: Source code to validate
            language: Programming language
            
        Returns:
            Validation results
        """
        if language.lower() == "python":
            try:
                ast.parse(code)
                return {"valid": True, "errors": []}
            except SyntaxError as e:
                return {
                    "valid": False,
                    "errors": [{
                        "line": e.lineno,
                        "message": e.msg,
                        "type": "SyntaxError"
                    }]
                }
        else:
            # For other languages, basic validation
            return {"valid": True, "errors": [], "note": f"Syntax validation for {language} not implemented"}
    
    def count_lines(self, code: str) -> Dict[str, int]:
        """
        Count different types of lines in code.
        
        Args:
            code: Source code
            
        Returns:
            Dictionary with line counts
        """
        lines = code.splitlines()
        
        counts = {
            "total": len(lines),
            "blank": 0,
            "comment": 0,
            "code": 0
        }
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                counts["blank"] += 1
            elif stripped.startswith("#") or stripped.startswith("//"):
                counts["comment"] += 1
            else:
                counts["code"] += 1
        
        return counts