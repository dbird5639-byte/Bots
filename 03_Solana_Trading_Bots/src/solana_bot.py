"""
Solana Trading Bot - Main Class

This is the main trading bot class for Solana blockchain trading,
including sniper bots, arbitrage, and MEV strategies.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import signal
import sys
from decimal import Decimal

from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey

from .config_manager import ConfigManager
from .logger import Logger
from .solana_connector import SolanaConnector
from .sniper_bot import SniperBot
from .arbitrage_bot import ArbitrageBot
from .mev_bot import MEVBot
from .risk_manager import RiskManager


class SolanaTradingBot:
    """
    Main Solana Trading Bot class
    
    This class orchestrates all Solana-specific trading components including:
    - Sniper bots for token launches
    - Arbitrage strategies across DEXs
    - MEV (Maximal Extractable Value) strategies
    - Risk management and portfolio optimization
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Solana Trading Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Solana components
        self.solana_connector: Optional[SolanaConnector] = None
        self.sniper_bot: Optional[SniperBot] = None
        self.arbitrage_bot: Optional[ArbitrageBot] = None
        self.mev_bot: Optional[MEVBot] = None
        self.risk_manager: Optional[RiskManager] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.trade_history = []
        self.sol_balance = Decimal('0')
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("Solana Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            self.log.info("Initializing Solana Trading Bot...")
            
            # Initialize Solana connection
            self.solana_connector = SolanaConnector(self.config, self.logger)
            await self.solana_connector.initialize()
            
            # Initialize trading bots
            self.sniper_bot = SniperBot(self.config, self.logger, self.solana_connector)
            self.arbitrage_bot = ArbitrageBot(self.config, self.logger, self.solana_connector)
            self.mev_bot = MEVBot(self.config, self.logger, self.solana_connector)
            self.risk_manager = RiskManager(self.config, self.logger)
            
            # Initialize each component
            await self.sniper_bot.initialize()
            await self.arbitrage_bot.initialize()
            await self.mev_bot.initialize()
            await self.risk_manager.initialize()
            
            # Check Solana balance
            await self._check_sol_balance()
            
            self.is_initialized = True
            self.log.info("Solana Trading Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Solana Trading Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the trading bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting Solana Trading Bot...")
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
            self.log.info("Stopping Solana Trading Bot...")
            self.is_running = False
            
            # Stop all components
            if self.sniper_bot:
                await self.sniper_bot.shutdown()
            if self.arbitrage_bot:
                await self.arbitrage_bot.shutdown()
            if self.mev_bot:
                await self.mev_bot.shutdown()
            if self.solana_connector:
                await self.solana_connector.shutdown()
            if self.risk_manager:
                await self.risk_manager.shutdown()
            
            self.log.info("Solana Trading Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _trading_loop(self):
        """Main trading loop for Solana strategies"""
        try:
            while self.is_running:
                # Check Solana network status
                network_status = await self.solana_connector.get_network_status()
                
                if network_status['is_healthy']:
                    # Execute sniper bot strategies
                    await self._execute_sniper_strategies()
                    
                    # Execute arbitrage strategies
                    await self._execute_arbitrage_strategies()
                    
                    # Execute MEV strategies
                    await self._execute_mev_strategies()
                    
                    # Update performance metrics
                    await self._update_performance_metrics()
                    
                    # Risk management check
                    await self._risk_management_check()
                    
                    # Check Solana balance
                    await self._check_sol_balance()
                else:
                    self.log.warning("Solana network unhealthy, waiting...")
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('trading.update_interval', 30))
                
        except Exception as e:
            self.log.error(f"Error in trading loop: {e}")
            await self.stop()
    
    async def _execute_sniper_strategies(self):
        """Execute sniper bot strategies"""
        try:
            if self.sniper_bot and self.sniper_bot.is_enabled():
                # Scan for new token launches
                new_launches = await self.sniper_bot.scan_new_launches()
                
                for launch in new_launches:
                    if await self.risk_manager.validate_sniper_opportunity(launch):
                        await self.sniper_bot.execute_snipe(launch)
                        
                        # Log the snipe
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'snipe',
                            'launch': launch,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed snipe: {launch['token_address']}")
                    else:
                        self.log.warning(f"Risk manager rejected snipe: {launch['token_address']}")
                        
        except Exception as e:
            self.log.error(f"Error executing sniper strategies: {e}")
    
    async def _execute_arbitrage_strategies(self):
        """Execute arbitrage strategies"""
        try:
            if self.arbitrage_bot and self.arbitrage_bot.is_enabled():
                # Scan for arbitrage opportunities
                opportunities = await self.arbitrage_bot.scan_opportunities()
                
                for opportunity in opportunities:
                    if await self.risk_manager.validate_arbitrage_opportunity(opportunity):
                        await self.arbitrage_bot.execute_arbitrage(opportunity)
                        
                        # Log the arbitrage
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'arbitrage',
                            'opportunity': opportunity,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed arbitrage: {opportunity['pair']}")
                    else:
                        self.log.warning(f"Risk manager rejected arbitrage: {opportunity['pair']}")
                        
        except Exception as e:
            self.log.error(f"Error executing arbitrage strategies: {e}")
    
    async def _execute_mev_strategies(self):
        """Execute MEV strategies"""
        try:
            if self.mev_bot and self.mev_bot.is_enabled():
                # Scan for MEV opportunities
                mev_opportunities = await self.mev_bot.scan_opportunities()
                
                for opportunity in mev_opportunities:
                    if await self.risk_manager.validate_mev_opportunity(opportunity):
                        await self.mev_bot.execute_mev(opportunity)
                        
                        # Log the MEV execution
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'mev',
                            'opportunity': opportunity,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed MEV: {opportunity['type']}")
                    else:
                        self.log.warning(f"Risk manager rejected MEV: {opportunity['type']}")
                        
        except Exception as e:
            self.log.error(f"Error executing MEV strategies: {e}")
    
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
            self.performance_metrics['sol_balance'] = float(self.sol_balance)
            
            # Log performance
            self.log.info(f"Performance metrics updated: {self.performance_metrics}")
            
        except Exception as e:
            self.log.error(f"Error updating performance metrics: {e}")
    
    async def _get_portfolio_performance(self) -> Dict[str, Any]:
        """Get current portfolio performance"""
        try:
            # Get token balances
            token_balances = await self.solana_connector.get_token_balances()
            
            # Calculate total value
            total_value = float(self.sol_balance)
            for token, balance in token_balances.items():
                if balance['usd_value']:
                    total_value += balance['usd_value']
            
            return {
                'total_value_usd': total_value,
                'sol_balance': float(self.sol_balance),
                'token_count': len(token_balances),
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
    
    async def _check_sol_balance(self):
        """Check current SOL balance"""
        try:
            self.sol_balance = await self.solana_connector.get_sol_balance()
            self.log.info(f"Current SOL balance: {self.sol_balance}")
            
        except Exception as e:
            self.log.error(f"Error checking SOL balance: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_trades': len(self.trade_history),
            'sol_balance': float(self.sol_balance),
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
    """Main function to run the Solana Trading Bot"""
    config_path = "config/config.yaml"
    
    async with SolanaTradingBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
