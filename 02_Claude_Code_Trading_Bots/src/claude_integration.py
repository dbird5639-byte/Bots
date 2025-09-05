"""
Claude Integration Module

This module handles all interactions with Claude AI for trading strategy
generation, market analysis, and code optimization.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import anthropic
from datetime import datetime

from .config_manager import ConfigManager
from .logger import Logger


class ClaudeIntegration:
    """Handles Claude AI integration for trading bot operations"""
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
        self.log = logging.getLogger(__name__)
        
        # Claude client
        self.client = None
        self.model = config.get('ai.claude.model', 'claude-3-sonnet-20240229')
        self.max_tokens = config.get('ai.claude.max_tokens', 4000)
        self.temperature = config.get('ai.claude.temperature', 0.1)
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = datetime.now()
        self.rate_limit = 50  # requests per minute
        
    async def initialize(self) -> bool:
        """Initialize Claude client"""
        try:
            api_key = self.config.get('ai.claude.api_key')
            if not api_key:
                self.log.error("Claude API key not configured")
                return False
            
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            self.log.info("Claude integration initialized successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Claude integration: {e}")
            return False
    
    async def generate_strategy_code(self, 
                                   strategy_type: str,
                                   market_conditions: Dict[str, Any],
                                   risk_preferences: Dict[str, Any]) -> Optional[str]:
        """Generate trading strategy code using Claude"""
        try:
            prompt = self._create_strategy_prompt(strategy_type, market_conditions, risk_preferences)
            
            response = await self._make_claude_request(prompt)
            if response:
                return self._extract_code_from_response(response)
            
            return None
            
        except Exception as e:
            self.log.error(f"Strategy generation failed: {e}")
            return None
    
    async def analyze_market(self, prompt: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions using Claude"""
        try:
            enhanced_prompt = f"{prompt}\n\nMarket Data: {market_data}"
            
            response = await self._make_claude_request(enhanced_prompt)
            if response:
                return self._parse_market_analysis(response)
            
            return {}
            
        except Exception as e:
            self.log.error(f"Market analysis failed: {e}")
            return {}
    
    async def get_recommendations(self, 
                                 prompt: str,
                                 portfolio_state: Dict[str, Any],
                                 market_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trading recommendations from Claude"""
        try:
            enhanced_prompt = f"{prompt}\n\nPortfolio: {portfolio_state}\nMarket: {market_conditions}"
            
            response = await self._make_claude_request(enhanced_prompt)
            if response:
                return self._parse_recommendations(response)
            
            return []
            
        except Exception as e:
            self.log.error(f"Recommendation generation failed: {e}")
            return []
    
    async def _make_claude_request(self, prompt: str) -> Optional[str]:
        """Make a request to Claude API with rate limiting"""
        try:
            # Rate limiting
            await self._check_rate_limit()
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            self.request_count += 1
            self.last_request_time = datetime.now()
            
            return response.content[0].text
            
        except Exception as e:
            self.log.error(f"Claude API request failed: {e}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = datetime.now()
        time_diff = (current_time - self.last_request_time).total_seconds()
        
        if time_diff < 60 and self.request_count >= self.rate_limit:
            wait_time = 60 - time_diff
            self.log.warning(f"Rate limit reached, waiting {wait_time} seconds")
            await asyncio.sleep(wait_time)
            self.request_count = 0
            self.last_request_time = datetime.now()
    
    def _create_strategy_prompt(self, 
                               strategy_type: str,
                               market_conditions: Dict[str, Any],
                               risk_preferences: Dict[str, Any]) -> str:
        """Create prompt for strategy generation"""
        return f"""
        Generate a Python trading strategy for {strategy_type} with the following requirements:
        
        Market Conditions: {market_conditions}
        Risk Preferences: {risk_preferences}
        
        Requirements:
        1. Use proper risk management
        2. Include position sizing
        3. Add stop-loss and take-profit logic
        4. Include performance tracking
        5. Follow Python best practices
        6. Add comprehensive comments
        
        Return only the Python code, no explanations.
        """
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from Claude response"""
        # Simple code extraction - look for Python code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        
        # Fallback: return the entire response
        return response.strip()
    
    def _parse_market_analysis(self, response: str) -> Dict[str, Any]:
        """Parse market analysis response from Claude"""
        # Simple parsing - can be enhanced
        return {
            'analysis': response,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.8  # Placeholder
        }
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse trading recommendations from Claude"""
        # Simple parsing - can be enhanced
        return [{
            'recommendation': response,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.8  # Placeholder
        }]
    
    async def shutdown(self):
        """Shutdown Claude integration"""
        try:
            if self.client:
                self.client.close()
            self.log.info("Claude integration shutdown completed")
        except Exception as e:
            self.log.error(f"Error during Claude shutdown: {e}")
