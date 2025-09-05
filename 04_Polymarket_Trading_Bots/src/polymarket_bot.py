"""
Polymarket Trading Bot - Main Class

This is the main trading bot class for Polymarket prediction markets,
including statistical arbitrage, copy trading, and market analysis.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import signal
import sys
from decimal import Decimal

import aiohttp
import pandas as pd

from .config_manager import ConfigManager
from .logger import Logger
from .polymarket_connector import PolymarketConnector
from .statistical_arbitrage import StatisticalArbitrage
from .copy_trading import CopyTrading
from .market_analyzer import MarketAnalyzer
from .risk_manager import RiskManager


class PolymarketTradingBot:
    """
    Main Polymarket Trading Bot class
    
    This class orchestrates all Polymarket-specific trading components including:
    - Statistical arbitrage across prediction markets
    - Copy trading from successful traders
    - Market analysis and sentiment tracking
    - Risk management and portfolio optimization
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Polymarket Trading Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Polymarket components
        self.polymarket_connector: Optional[PolymarketConnector] = None
        self.statistical_arbitrage: Optional[StatisticalArbitrage] = None
        self.copy_trading: Optional[CopyTrading] = None
        self.market_analyzer: Optional[MarketAnalyzer] = None
        self.risk_manager: Optional[RiskManager] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.trade_history = []
        self.usdc_balance = Decimal('0')
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("Polymarket Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            self.log.info("Initializing Polymarket Trading Bot...")
            
            # Initialize Polymarket connection
            self.polymarket_connector = PolymarketConnector(self.config, self.logger)
            await self.polymarket_connector.initialize()
            
            # Initialize trading components
            self.statistical_arbitrage = StatisticalArbitrage(self.config, self.logger, self.polymarket_connector)
            self.copy_trading = CopyTrading(self.config, self.logger, self.polymarket_connector)
            self.market_analyzer = MarketAnalyzer(self.config, self.logger, self.polymarket_connector)
            self.risk_manager = RiskManager(self.config, self.logger)
            
            # Initialize each component
            await self.statistical_arbitrage.initialize()
            await self.copy_trading.initialize()
            await self.market_analyzer.initialize()
            await self.risk_manager.initialize()
            
            # Check USDC balance
            await self._check_usdc_balance()
            
            self.is_initialized = True
            self.log.info("Polymarket Trading Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Polymarket Trading Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the trading bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting Polymarket Trading Bot...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start main trading loop
            await self._trading_loop()
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to start trading bot: {e}")
            return False
    
    async def stop(self):
        """Stop the trading bot gracefully"""
        try:
            self.log.info("Stopping Polymarket Trading Bot...")
            self.is_running = False
            
            # Stop all components
            if self.statistical_arbitrage:
                await self.statistical_arbitrage.shutdown()
            if self.copy_trading:
                await self.copy_trading.shutdown()
            if self.market_analyzer:
                await self.market_analyzer.shutdown()
            if self.polymarket_connector:
                await self.polymarket_connector.shutdown()
            if self.risk_manager:
                await self.risk_manager.shutdown()
            
            self.log.info("Polymarket Trading Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _trading_loop(self):
        """Main trading loop for Polymarket strategies"""
        try:
            while self.is_running:
                # Get market data
                market_data = await self.polymarket_connector.get_market_data()
                
                # Analyze markets
                market_analysis = await self.market_analyzer.analyze_markets(market_data)
                
                # Execute statistical arbitrage
                await self._execute_statistical_arbitrage(market_analysis)
                
                # Execute copy trading
                await self._execute_copy_trading(market_analysis)
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Risk management check
                await self._risk_management_check()
                
                # Check USDC balance
                await self._check_usdc_balance()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('trading.update_interval', 60))
                
        except Exception as e:
            self.log.error(f"Error in trading loop: {e}")
            await self.stop()
    
    async def _execute_statistical_arbitrage(self, market_analysis: Dict[str, Any]):
        """Execute statistical arbitrage strategies"""
        try:
            if self.statistical_arbitrage and self.statistical_arbitrage.is_enabled():
                # Find arbitrage opportunities
                opportunities = await self.statistical_arbitrage.find_opportunities(market_analysis)
                
                for opportunity in opportunities:
                    if await self.risk_manager.validate_arbitrage_opportunity(opportunity):
                        await self.statistical_arbitrage.execute_arbitrage(opportunity)
                        
                        # Log the arbitrage
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'statistical_arbitrage',
                            'opportunity': opportunity,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed arbitrage: {opportunity['markets']}")
                    else:
                        self.log.warning(f"Risk manager rejected arbitrage: {opportunity['markets']}")
                        
        except Exception as e:
            self.log.error(f"Error executing statistical arbitrage: {e}")
    
    async def _execute_copy_trading(self, market_analysis: Dict[str, Any]):
        """Execute copy trading strategies"""
        try:
            if self.copy_trading and self.copy_trading.is_enabled():
                # Find copy trading opportunities
                opportunities = await self.copy_trading.find_opportunities(market_analysis)
                
                for opportunity in opportunities:
                    if await self.risk_manager.validate_copy_trading_opportunity(opportunity):
                        await self.copy_trading.execute_copy_trade(opportunity)
                        
                        # Log the copy trade
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'copy_trading',
                            'opportunity': opportunity,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed copy trade: {opportunity['trader']}")
                    else:
                        self.log.warning(f"Risk manager rejected copy trade: {opportunity['trader']}")
                        
        except Exception as e:
            self.log.error(f"Error executing copy trading: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get current portfolio performance
            portfolio_performance = await self._get_portfolio_performance()
            
            # Update metrics
            self.performance_metrics.update(portfolio_performance)
            self.performance_metrics['uptime'] = (
                datetime.now() - self.start_time
            ).total_seconds() if self.start_time else 0
            self.performance_metrics['usdc_balance'] = float(self.usdc_balance)
            
            # Log performance
            self.log.info(f"Performance metrics updated: {self.performance_metrics}")
            
        except Exception as e:
            self.log.error(f"Error updating performance metrics: {e}")
    
    async def _get_portfolio_performance(self) -> Dict[str, Any]:
        """Get current portfolio performance"""
        try:
            # Get position balances
            positions = await self.polymarket_connector.get_positions()
            
            # Calculate total value
            total_value = float(self.usdc_balance)
            for position in positions:
                if position['usdc_value']:
                    total_value += position['usdc_value']
            
            return {
                'total_value_usdc': total_value,
                'usdc_balance': float(self.usdc_balance),
                'position_count': len(positions),
                'total_trades': len(self.trade_history)
            }
            
        except Exception as e:
            self.log.error(f"Error getting portfolio performance: {e}")
            return {}
    
    async def _risk_management_check(self):
        """Perform risk management checks"""
        try:
            # Check portfolio risk levels
            risk_assessment = await self.risk_manager.assess_portfolio_risk()
            
            if risk_assessment['risk_level'] == 'high':
                self.log.warning("High risk detected, taking protective measures")
                await self._take_protective_measures()
            
        except Exception as e:
            self.log.error(f"Error in risk management check: {e}")
    
    async def _take_protective_measures(self):
        """Take protective measures when risk is high"""
        try:
            # Close high-risk positions
            await self._close_high_risk_positions()
            
            # Reduce position sizes
            await self._reduce_position_sizes()
            
            # Notify administrators
            await self._send_risk_alert()
            
        except Exception as e:
            self.log.error(f"Error taking protective measures: {e}")
    
    async def _close_high_risk_positions(self):
        """Close high-risk positions"""
        # TODO: Implement position closing logic
        self.log.info("Closing high-risk positions")
    
    async def _reduce_position_sizes(self):
        """Reduce position sizes"""
        # TODO: Implement position size reduction
        self.log.info("Reducing position sizes")
    
    async def _send_risk_alert(self):
        """Send risk alert notifications"""
        # TODO: Implement alert system
        self.log.warning("RISK ALERT: High risk conditions detected")
    
    async def _check_usdc_balance(self):
        """Check current USDC balance"""
        try:
            self.usdc_balance = await self.polymarket_connector.get_usdc_balance()
            self.log.info(f"Current USDC balance: {self.usdc_balance}")
            
        except Exception as e:
            self.log.error(f"Error checking USDC balance: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_trades': len(self.trade_history),
            'usdc_balance': float(self.usdc_balance),
            'performance_metrics': self.performance_metrics
        }
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.log.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.stop())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


# Main execution function
async def main():
    """Main function to run the Polymarket Trading Bot"""
    config_path = "config/config.yaml"
    
    async with PolymarketTradingBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
