"""
Claude Trading Bot - Main Class

This module contains the main trading bot class that orchestrates
all AI components, market data, risk management, and trade execution.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import signal
import sys

from .ai_manager import AIManager
from .strategy_executor import StrategyExecutor
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager
from .data_manager import DataManager
from .market_analyzer import MarketAnalyzer
from .performance_tracker import PerformanceTracker
from .config_manager import ConfigManager
from .logger import Logger


class ClaudeTradingBot:
    """
    Main trading bot class that coordinates all trading operations.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Claude Trading Bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        self.config = ConfigManager(config_path)
        
        # Initialize logger
        self.logger = Logger(
            name="ClaudeTradingBot",
            log_level=self.config.get('bot.log_level', 'INFO'),
            log_file=self.config.get('logging.file_path', 'logs/trading_bot.log')
        )
        
        # Initialize components
        self.ai_manager = None
        self.strategy_executor = StrategyExecutor()
        self.risk_manager = RiskManager(
            max_portfolio_risk=self.config.get('trading.max_portfolio_risk', 0.05),
            max_position_risk=self.config.get('trading.default_risk_per_trade', 0.01)
        )
        self.portfolio_manager = PortfolioManager(
            initial_capital=self.config.get('trading.initial_capital', 10000.0)
        )
        self.data_manager = DataManager()
        self.market_analyzer = MarketAnalyzer()
        self.performance_tracker = PerformanceTracker()
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.trading_enabled = self.config.get('trading.enabled', False)
        self.paper_trading = self.config.get('trading.paper_trading', True)
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.logger.info("Claude Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all bot components.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("Initializing Claude Trading Bot...")
            
            # Initialize AI manager
            claude_api_key = self.config.get('ai.claude_api_key')
            if not claude_api_key:
                self.logger.error("Claude API key not configured")
                return False
            
            self.ai_manager = AIManager(claude_api_key)
            await self.ai_manager.initialize()
            
            # Initialize data sources
            data_sources = self.config.get('data.sources', [])
            for source in data_sources:
                self.data_manager.add_data_source(source, {})
            
            self.is_initialized = True
            self.logger.info("Claude Trading Bot initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    async def start(self):
        """Start the trading bot."""
        try:
            if not self.is_initialized:
                if not await self.initialize():
                    raise RuntimeError("Failed to initialize bot")
            
            if not self.trading_enabled:
                self.logger.warning("Trading is disabled in configuration")
                return
            
            self.is_running = True
            self.logger.info("Starting Claude Trading Bot...")
            
            # Start main trading loop
            await self._trading_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the trading bot."""
        try:
            self.is_running = False
            self.logger.info("Stopping Claude Trading Bot...")
            
            # Shutdown AI manager
            if self.ai_manager:
                await self.ai_manager.shutdown()
            
            # Close logger
            self.logger.close()
            
            self.logger.info("Claude Trading Bot stopped")
            
        except Exception as e:
            print(f"Error stopping bot: {e}")
    
    async def _trading_loop(self):
        """Main trading loop."""
        try:
            while self.is_running:
                # Get market data
                market_data = await self._get_market_data()
                
                # Analyze market conditions
                market_analysis = self.market_analyzer.analyze_market_conditions(market_data)
                
                # Get AI recommendations
                portfolio_state = self.portfolio_manager.get_portfolio_summary()
                recommendations = await self.ai_manager.get_trading_recommendations(
                    portfolio_state, market_analysis
                )
                
                # Process recommendations
                await self._process_recommendations(recommendations, market_data)
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Risk management check
                await self._risk_management_check()
                
                # Wait for next iteration
                update_interval = self.config.get('data.update_interval', 60)
                await asyncio.sleep(update_interval)
                
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}")
            raise
    
    async def _get_market_data(self) -> List[Dict[str, Any]]:
        """Get market data for analysis."""
        try:
            symbols = self.config.get('trading.symbols', ['BTC/USD', 'ETH/USD'])
            market_data = []
            
            for symbol in symbols:
                data = await self.data_manager.fetch_market_data(symbol, 'price', '1m', 100)
                if data:
                    market_data.extend(data)
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return []
    
    async def _process_recommendations(self, recommendations: List[Dict[str, Any]], 
                                     market_data: List[Dict[str, Any]]):
        """Process AI trading recommendations."""
        try:
            for recommendation in recommendations:
                # Validate recommendation
                if not self._validate_recommendation(recommendation):
                    continue
                
                # Check risk limits
                risk_check = self.risk_manager.validate_trade_risk(
                    recommendation, self.portfolio_manager.get_portfolio_summary()
                )
                
                if not risk_check['is_valid']:
                    self.logger.warning(f"Risk check failed: {risk_check['reason']}")
                    continue
                
                # Execute strategy if approved
                if recommendation.get('action') in ['buy', 'sell']:
                    await self._execute_trade(recommendation, market_data)
                
        except Exception as e:
            self.logger.error(f"Error processing recommendations: {e}")
    
    def _validate_recommendation(self, recommendation: Dict[str, Any]) -> bool:
        """Validate trading recommendation."""
        required_fields = ['action', 'symbol', 'confidence', 'reasoning']
        
        for field in required_fields:
            if field not in recommendation:
                self.logger.warning(f"Recommendation missing required field: {field}")
                return False
        
        # Check confidence threshold
        confidence = recommendation.get('confidence', 0)
        min_confidence = self.config.get('trading.min_confidence', 0.7)
        
        if confidence < min_confidence:
            self.logger.debug(f"Recommendation confidence too low: {confidence}")
            return False
        
        return True
    
    async def _execute_trade(self, recommendation: Dict[str, Any], 
                           market_data: List[Dict[str, Any]]):
        """Execute a trade based on recommendation."""
        try:
            action = recommendation['action']
            symbol = recommendation['symbol']
            confidence = recommendation['confidence']
            
            self.logger.info(f"Executing {action} trade for {symbol} (confidence: {confidence})")
            
            # Get current market price
            current_price = self._get_current_price(symbol, market_data)
            if not current_price:
                self.logger.warning(f"Could not get current price for {symbol}")
                return
            
            # Calculate position size
            capital = self.portfolio_manager.current_capital
            risk_per_trade = self.config.get('trading.default_risk_per_trade', 0.01)
            
            # For demo purposes, use fixed position size
            position_size = capital * 0.1  # 10% of capital
            
            # Create trade data
            trade_data = {
                'symbol': symbol,
                'action': action,
                'price': current_price,
                'quantity': position_size / current_price,
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence,
                'reasoning': recommendation.get('reasoning', '')
            }
            
            # Execute trade
            if self.paper_trading:
                await self._execute_paper_trade(trade_data)
            else:
                # Real trading implementation would go here
                self.logger.warning("Real trading not implemented")
            
            # Log trade
            self.logger.log_trade(trade_data)
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
    
    def _get_current_price(self, symbol: str, market_data: List[Dict[str, Any]]) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            for data_point in market_data:
                if data_point.get('symbol') == symbol:
                    return float(data_point.get('price', 0))
            return None
        except Exception:
            return None
    
    async def _execute_paper_trade(self, trade_data: Dict[str, Any]):
        """Execute a paper trade (simulation)."""
        try:
            symbol = trade_data['symbol']
            action = trade_data['action']
            price = trade_data['price']
            quantity = trade_data['quantity']
            
            if action == 'buy':
                # Add position to portfolio
                self.portfolio_manager.add_position(
                    symbol, quantity, price, 'long'
                )
                self.logger.info(f"Paper trade: Bought {quantity} {symbol} @ {price}")
                
            elif action == 'sell':
                # Close position in portfolio
                open_positions = self.portfolio_manager.get_open_positions()
                for position in open_positions:
                    if position['symbol'] == symbol:
                        self.portfolio_manager.close_position(position['id'], price)
                        self.logger.info(f"Paper trade: Sold {quantity} {symbol} @ {price}")
                        break
            
            # Add to performance tracker
            self.performance_tracker.add_trade({
                'symbol': symbol,
                'entry_time': trade_data['timestamp'],
                'entry_price': price,
                'quantity': quantity,
                'position_type': 'long' if action == 'buy' else 'short',
                'status': 'closed' if action == 'sell' else 'open'
            })
            
        except Exception as e:
            self.logger.error(f"Error executing paper trade: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            self.logger.log_performance(portfolio_summary)
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    async def _risk_management_check(self):
        """Perform risk management checks."""
        try:
            portfolio_state = self.portfolio_manager.get_portfolio_summary()
            
            # Check portfolio risk
            if portfolio_state['total_return'] < -20:  # 20% loss threshold
                self.logger.warning("Portfolio loss threshold exceeded")
                await self._take_protective_measures()
            
            # Check individual position risks
            open_positions = self.portfolio_manager.get_open_positions()
            for position in open_positions:
                # Calculate current PnL
                current_price = self._get_current_price(position['symbol'], [])
                if current_price:
                    unrealized_pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = (unrealized_pnl / (position['entry_price'] * position['quantity'])) * 100
                    
                    # Close position if loss exceeds threshold
                    if pnl_percent < -10:  # 10% loss threshold
                        self.logger.warning(f"Closing position {position['symbol']} due to loss: {pnl_percent:.2f}%")
                        self.portfolio_manager.close_position(position['id'], current_price)
            
        except Exception as e:
            self.logger.error(f"Error in risk management check: {e}")
    
    async def _take_protective_measures(self):
        """Take protective measures when risk thresholds are exceeded."""
        try:
            self.logger.warning("Taking protective measures...")
            
            # Close all open positions
            open_positions = self.portfolio_manager.get_open_positions()
            for position in open_positions:
                current_price = self._get_current_price(position['symbol'], [])
                if current_price:
                    self.portfolio_manager.close_position(position['id'], current_price)
            
            # Pause trading temporarily
            self.trading_enabled = False
            self.logger.info("Trading paused due to risk threshold")
            
            # Wait before resuming
            await asyncio.sleep(300)  # 5 minutes
            self.trading_enabled = True
            self.logger.info("Trading resumed")
            
        except Exception as e:
            self.logger.error(f"Error taking protective measures: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status."""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'trading_enabled': self.trading_enabled,
            'paper_trading': self.paper_trading,
            'portfolio_summary': self.portfolio_manager.get_portfolio_summary(),
            'performance_metrics': self.performance_tracker.get_performance_summary(),
            'ai_status': self.ai_manager.get_ai_status() if self.ai_manager else {},
            'risk_metrics': self.risk_manager.get_risk_metrics(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.stop())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


async def main():
    """Main function to run the trading bot."""
    try:
        async with ClaudeTradingBot() as bot:
            await bot.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
