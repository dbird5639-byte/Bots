"""
Code Optimizer Module

This module handles code optimization and performance improvements
for trading strategies using AI analysis.
"""

import logging
from typing import Dict, Any, Optional, List
import ast
import re


class CodeOptimizer:
    """
    Optimizes trading strategy code for performance and reliability.
    """
    
    def __init__(self):
        """Initialize the code optimizer."""
        self.logger = logging.getLogger(__name__)
        self.optimization_suggestions = []
    
    def optimize_strategy_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze and optimize trading strategy code.
        
        Args:
            code: Python code string to optimize
            
        Returns:
            Optimization results and suggestions
        """
        try:
            # Parse code for analysis
            tree = ast.parse(code)
            
            # Analyze code structure
            analysis = self._analyze_code_structure(tree)
            
            # Generate optimization suggestions
            suggestions = self._generate_suggestions(analysis)
            
            # Apply optimizations
            optimized_code = self._apply_optimizations(code, suggestions)
            
            return {
                'original_code': code,
                'optimized_code': optimized_code,
                'suggestions': suggestions,
                'improvements': len(suggestions)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing code: {e}")
            return {
                'original_code': code,
                'optimized_code': code,
                'suggestions': [],
                'improvements': 0,
                'error': str(e)
            }
    
    def _analyze_code_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze the structure of the code."""
        analysis = {
            'functions': 0,
            'loops': 0,
            'conditionals': 0,
            'imports': 0,
            'variables': 0,
            'complexity': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'] += 1
            elif isinstance(node, (ast.For, ast.While)):
                analysis['loops'] += 1
            elif isinstance(node, ast.If):
                analysis['conditionals'] += 1
            elif isinstance(node, ast.Import):
                analysis['imports'] += 1
            elif isinstance(node, ast.Assign):
                analysis['variables'] += 1
        
        # Calculate complexity score
        analysis['complexity'] = analysis['functions'] + analysis['loops'] * 2 + analysis['conditionals']
        
        return analysis
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        if analysis['complexity'] > 10:
            suggestions.append("Consider breaking down complex functions into smaller, focused functions")
        
        if analysis['loops'] > 5:
            suggestions.append("Optimize loops with vectorized operations where possible")
        
        if analysis['conditionals'] > 8:
            suggestions.append("Simplify conditional logic with lookup tables or strategy patterns")
        
        if analysis['imports'] > 10:
            suggestions.append("Consolidate imports and remove unused dependencies")
        
        return suggestions
    
    def _apply_optimizations(self, code: str, suggestions: List[str]) -> str:
        """Apply basic optimizations to the code."""
        optimized_code = code
        
        # Remove trailing whitespace
        optimized_code = re.sub(r'[ \t]+$', '', optimized_code, flags=re.MULTILINE)
        
        # Remove multiple blank lines
        optimized_code = re.sub(r'\n\s*\n\s*\n', '\n\n', optimized_code)
        
        return optimized_code
    
    def validate_code_safety(self, code: str) -> Dict[str, Any]:
        """
        Validate code for safety and best practices.
        
        Args:
            code: Python code to validate
            
        Returns:
            Validation results
        """
        safety_checks = {
            'has_error_handling': 'try:' in code or 'except:' in code,
            'has_logging': 'logging' in code or 'logger' in code,
            'has_validation': 'assert' in code or 'isinstance' in code,
            'has_timeouts': 'timeout' in code.lower(),
            'has_rate_limiting': 'rate' in code.lower() and 'limit' in code.lower()
        }
        
        return {
            'is_safe': all(safety_checks.values()),
            'checks': safety_checks,
            'score': sum(safety_checks.values()) / len(safety_checks)
        }
