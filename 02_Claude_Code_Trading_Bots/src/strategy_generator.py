"""
Strategy Generator Module

This module handles the generation and optimization of trading strategies
using Claude AI and other AI models.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re

from .claude_integration import ClaudeIntegration


class StrategyGenerator:
    """
    Generates and optimizes trading strategies using AI models.
    """
    
    def __init__(self, claude_integration: ClaudeIntegration):
        """
        Initialize the strategy generator.
        
        Args:
            claude_integration: Claude AI integration instance
        """
        self.claude_integration = claude_integration
        self.logger = logging.getLogger(__name__)
        self.generated_strategies = {}
        self.strategy_performance = {}
        
    async def generate_strategy(self, 
                              market_conditions: Dict[str, Any],
                              risk_profile: str,
                              capital: float,
                              timeframe: str) -> Dict[str, Any]:
        """
        Generate a new trading strategy based on market conditions.
        
        Args:
            market_conditions: Current market data and conditions
            risk_profile: Risk tolerance level (low, medium, high)
            capital: Available capital for trading
            timeframe: Trading timeframe (1m, 5m, 1h, 1d, etc.)
            
        Returns:
            Generated strategy configuration
        """
        try:
            self.logger.info(f"Generating strategy for {risk_profile} risk profile")
            
            # Create strategy prompt
            prompt = self._create_strategy_prompt(
                market_conditions, risk_profile, capital, timeframe
            )
            
            # Generate strategy using Claude
            response = await self.claude_integration.generate_strategy_code(prompt)
            
            # Parse and validate strategy
            strategy = self._parse_strategy_response(response)
            
            # Add metadata
            strategy['id'] = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            strategy['generated_at'] = datetime.now().isoformat()
            strategy['market_conditions'] = market_conditions
            strategy['risk_profile'] = risk_profile
            strategy['capital'] = capital
            strategy['timeframe'] = timeframe
            
            # Store strategy
            self.generated_strategies[strategy['id']] = strategy
            
            self.logger.info(f"Generated strategy {strategy['id']}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error generating strategy: {e}")
            raise
    
    async def optimize_strategy(self, 
                              strategy_id: str,
                              performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize an existing strategy based on performance data.
        
        Args:
            strategy_id: ID of the strategy to optimize
            performance_data: Historical performance metrics
            
        Returns:
            Optimized strategy configuration
        """
        try:
            if strategy_id not in self.generated_strategies:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            original_strategy = self.generated_strategies[strategy_id]
            
            self.logger.info(f"Optimizing strategy {strategy_id}")
            
            # Create optimization prompt
            prompt = self._create_optimization_prompt(
                original_strategy, performance_data
            )
            
            # Generate optimized strategy
            response = await self.claude_integration.generate_strategy_code(prompt)
            
            # Parse optimized strategy
            optimized_strategy = self._parse_strategy_response(response)
            
            # Add optimization metadata
            optimized_strategy['id'] = f"{strategy_id}_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            optimized_strategy['original_strategy_id'] = strategy_id
            optimized_strategy['optimized_at'] = datetime.now().isoformat()
            optimized_strategy['optimization_data'] = performance_data
            
            # Store optimized strategy
            self.generated_strategies[optimized_strategy['id']] = optimized_strategy
            
            self.logger.info(f"Optimized strategy {optimized_strategy['id']}")
            return optimized_strategy
            
        except Exception as e:
            self.logger.error(f"Error optimizing strategy: {e}")
            raise
    
    def _create_strategy_prompt(self,
                               market_conditions: Dict[str, Any],
                               risk_profile: str,
                               capital: float,
                               timeframe: str) -> str:
        """
        Create a prompt for strategy generation.
        
        Args:
            market_conditions: Market data and conditions
            risk_profile: Risk tolerance level
            capital: Available capital
            timeframe: Trading timeframe
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
        Generate a trading strategy with the following requirements:
        
        Market Conditions:
        {json.dumps(market_conditions, indent=2)}
        
        Risk Profile: {risk_profile}
        Available Capital: ${capital:,.2f}
        Timeframe: {timeframe}
        
        Please provide:
        1. Strategy name and description
        2. Entry and exit conditions
        3. Position sizing rules
        4. Risk management parameters
        5. Python code implementation
        6. Expected performance metrics
        
        The strategy should be suitable for automated trading and include proper error handling.
        """
        
        return prompt.strip()
    
    def _create_optimization_prompt(self,
                                   original_strategy: Dict[str, Any],
                                   performance_data: Dict[str, Any]) -> str:
        """
        Create a prompt for strategy optimization.
        
        Args:
            original_strategy: Original strategy configuration
            performance_data: Historical performance metrics
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
        Optimize the following trading strategy based on performance data:
        
        Original Strategy:
        {json.dumps(original_strategy, indent=2)}
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Please identify areas for improvement and provide:
        1. Optimized entry/exit conditions
        2. Better risk management parameters
        3. Improved position sizing
        4. Enhanced Python code implementation
        5. Expected performance improvements
        
        Focus on fixing any issues found in the performance data.
        """
        
        return prompt.strip()
    
    def _parse_strategy_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response into a structured strategy.
        
        Args:
            response: Raw AI response
            
        Returns:
            Parsed strategy dictionary
        """
        try:
            # Extract code blocks
            code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
            
            # Extract strategy components
            strategy = {
                'name': self._extract_field(response, 'Strategy Name:', 'Strategy:'),
                'description': self._extract_field(response, 'Description:', 'Strategy Description:'),
                'entry_conditions': self._extract_field(response, 'Entry Conditions:', 'Entry:'),
                'exit_conditions': self._extract_field(response, 'Exit Conditions:', 'Exit:'),
                'position_sizing': self._extract_field(response, 'Position Sizing:', 'Sizing:'),
                'risk_management': self._extract_field(response, 'Risk Management:', 'Risk:'),
                'code': code_blocks[0] if code_blocks else '',
                'expected_metrics': self._extract_metrics(response)
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error parsing strategy response: {e}")
            # Return basic structure if parsing fails
            return {
                'name': 'Generated Strategy',
                'description': 'AI-generated trading strategy',
                'entry_conditions': 'Market analysis based',
                'exit_conditions': 'Risk management based',
                'position_sizing': 'Capital percentage based',
                'risk_management': 'Stop loss and take profit',
                'code': response,
                'expected_metrics': {}
            }
    
    def _extract_field(self, text: str, *field_names: str) -> str:
        """
        Extract a field value from text.
        
        Args:
            text: Text to search in
            *field_names: Possible field names to search for
            
        Returns:
            Extracted field value or empty string
        """
        for field_name in field_names:
            if field_name in text:
                start = text.find(field_name) + len(field_name)
                end = text.find('\n', start)
                if end == -1:
                    end = len(text)
                return text[start:end].strip()
        return ''
    
    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extract expected performance metrics from text.
        
        Args:
            text: Text to search in
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Look for common metric patterns
        metric_patterns = [
            r'Expected Return:\s*([\d.]+)%',
            r'Max Drawdown:\s*([\d.]+)%',
            r'Sharpe Ratio:\s*([\d.]+)',
            r'Win Rate:\s*([\d.]+)%'
        ]
        
        for pattern in metric_patterns:
            match = re.search(pattern, text)
            if match:
                metric_name = pattern.split(':')[0].strip()
                value = float(match.group(1))
                metrics[metric_name] = value
        
        return metrics
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a generated strategy by ID.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy configuration or None
        """
        return self.generated_strategies.get(strategy_id)
    
    def list_strategies(self) -> List[str]:
        """
        Get list of all generated strategy IDs.
        
        Returns:
            List of strategy IDs
        """
        return list(self.generated_strategies.keys())
    
    def update_performance(self, strategy_id: str, performance: Dict[str, Any]):
        """
        Update performance data for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            performance: Performance metrics
        """
        if strategy_id in self.generated_strategies:
            self.strategy_performance[strategy_id] = performance
            self.logger.info(f"Updated performance for strategy {strategy_id}")
    
    def get_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance data for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Performance data or None
        """
        return self.strategy_performance.get(strategy_id)
