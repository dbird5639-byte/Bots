"""
AI Manager Module

This module coordinates all AI components and manages
the overall AI-powered trading system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .claude_integration import ClaudeIntegration
from .strategy_generator import StrategyGenerator
from .code_optimizer import CodeOptimizer


class AIManager:
    """
    Manages all AI components and coordinates their interactions.
    """
    
    def __init__(self, claude_api_key: str):
        """
        Initialize the AI manager.
        
        Args:
            claude_api_key: Claude API key for authentication
        """
        self.logger = logging.getLogger(__name__)
        self.claude_integration = ClaudeIntegration(claude_api_key)
        self.strategy_generator = StrategyGenerator(self.claude_integration)
        self.code_optimizer = CodeOptimizer()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all AI components."""
        try:
            await self.claude_integration.initialize()
            self.is_initialized = True
            self.logger.info("AI Manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Manager: {e}")
            return False
    
    async def generate_and_optimize_strategy(self,
                                           market_conditions: Dict[str, Any],
                                           risk_profile: str,
                                           capital: float,
                                           timeframe: str) -> Dict[str, Any]:
        """
        Generate and optimize a trading strategy using AI.
        
        Args:
            market_conditions: Current market data
            risk_profile: Risk tolerance level
            capital: Available capital
            timeframe: Trading timeframe
            
        Returns:
            Generated and optimized strategy
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("AI Manager not initialized")
            
            # Generate strategy
            strategy = await self.strategy_generator.generate_strategy(
                market_conditions, risk_profile, capital, timeframe
            )
            
            # Optimize code
            optimization_result = self.code_optimizer.optimize_strategy_code(
                strategy.get('code', '')
            )
            
            # Update strategy with optimized code
            strategy['optimized_code'] = optimization_result.get('optimized_code', '')
            strategy['optimization_suggestions'] = optimization_result.get('suggestions', [])
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error in strategy generation: {e}")
            raise
    
    async def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market conditions using AI.
        
        Args:
            market_data: Market data to analyze
            
        Returns:
            Market analysis results
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("AI Manager not initialized")
            
            analysis = await self.claude_integration.analyze_market(market_data)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {e}")
            raise
    
    async def get_trading_recommendations(self, 
                                        portfolio_state: Dict[str, Any],
                                        market_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get AI-powered trading recommendations.
        
        Args:
            portfolio_state: Current portfolio state
            market_conditions: Current market conditions
            
        Returns:
            List of trading recommendations
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("AI Manager not initialized")
            
            recommendations = await self.claude_integration.get_recommendations(
                portfolio_state, market_conditions
            )
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            raise
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get the status of all AI components."""
        return {
            'is_initialized': self.is_initialized,
            'claude_status': self.claude_integration.get_status(),
            'strategy_generator_status': {
                'total_strategies': len(self.strategy_generator.generated_strategies),
                'active_strategies': len(self.strategy_generator.generated_strategies)
            },
            'code_optimizer_status': {
                'total_optimizations': len(self.code_optimizer.optimization_suggestions)
            }
        }
    
    async def shutdown(self):
        """Shutdown all AI components."""
        try:
            await self.claude_integration.shutdown()
            self.is_initialized = False
            self.logger.info("AI Manager shutdown successfully")
        except Exception as e:
            self.logger.error(f"Error during AI Manager shutdown: {e}")
