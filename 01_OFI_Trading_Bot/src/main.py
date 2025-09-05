#!/usr/bin/env python3
"""
OFI Trading Bot - Main Entry Point

This is the main entry point for the Order Flow Imbalance trading bot.
It orchestrates all components and manages the bot's lifecycle.
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.exchange_connector import ExchangeConnector
from src.ofi_analyzer import OFIAnalyzer
from src.signal_generator import SignalGenerator
from src.risk_manager import RiskManager


class TradingBot:
    """
    Main trading bot class that orchestrates all components.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the trading bot with configuration."""
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.exchange_connector = None
        self.ofi_analyzer = None
        self.signal_generator = None
        self.risk_manager = None
        self.running = False
        self.tasks = []
        
    async def initialize(self):
        """Initialize all bot components."""
        try:
            # Load configuration
            self.config = ConfigLoader.load_config(self.config_path)
            
            # Setup logging
            self.logger = setup_logger(
                level=self.config.get("logging.level", "INFO"),
                file_path=self.config.get("logging.file_path", "logs/trading_bot.log")
            )
            
            self.logger.info("Initializing OFI Trading Bot...")
            
            # Initialize exchange connector
            self.exchange_connector = ExchangeConnector(self.config)
            await self.exchange_connector.initialize()
            
            # Initialize OFI analyzer
            self.ofi_analyzer = OFIAnalyzer(self.config)
            
            # Initialize signal generator
            self.signal_generator = SignalGenerator(self.config)
            
            # Initialize risk manager
            self.risk_manager = RiskManager(self.config)
            
            self.logger.info("Bot initialization completed successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize bot: {e}")
            else:
                print(f"Failed to initialize bot: {e}")
            raise
    
    async def start(self):
        """Start the trading bot."""
        try:
            self.logger.info("Starting OFI Trading Bot...")
            self.running = True
            
            # Start exchange data streaming
            await self.exchange_connector.start_streaming()
            
            # Start main trading loop
            main_task = asyncio.create_task(self.trading_loop())
            self.tasks.append(main_task)
            
            # Start monitoring tasks
            monitor_task = asyncio.create_task(self.monitoring_loop())
            self.tasks.append(monitor_task)
            
            self.logger.info("Bot started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the trading bot gracefully."""
        try:
            self.logger.info("Stopping OFI Trading Bot...")
            self.running = False
            
            # Cancel all running tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)
            
            # Stop exchange connector
            if self.exchange_connector:
                await self.exchange_connector.stop()
            
            self.logger.info("Bot stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    async def trading_loop(self):
        """Main trading loop that processes market data and executes trades."""
        while self.running:
            try:
                # Get latest market data
                market_data = await self.exchange_connector.get_market_data()
                
                if market_data:
                    # Analyze order flow imbalance
                    ofi_signals = await self.ofi_analyzer.analyze(market_data)
                    
                    # Generate trading signals
                    trading_signals = await self.signal_generator.generate_signals(ofi_signals)
                    
                    # Apply risk management
                    approved_signals = await self.risk_manager.validate_signals(trading_signals)
                    
                    # Execute approved trades
                    if approved_signals:
                        await self.execute_trades(approved_signals)
                
                # Wait before next iteration
                await asyncio.sleep(1)  # 1 second interval
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def monitoring_loop(self):
        """Monitoring loop for bot health and performance."""
        while self.running:
            try:
                # Check bot health
                health_status = await self.check_health()
                
                # Log performance metrics
                await self.log_performance_metrics()
                
                # Check risk limits
                await self.check_risk_limits()
                
                # Wait before next check
                await asyncio.sleep(30)  # 30 second interval
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def execute_trades(self, signals):
        """Execute approved trading signals."""
        for signal in signals:
            try:
                self.logger.info(f"Executing trade signal: {signal}")
                
                # Execute the trade through exchange connector
                result = await self.exchange_connector.execute_trade(signal)
                
                if result:
                    self.logger.info(f"Trade executed successfully: {result}")
                else:
                    self.logger.warning(f"Trade execution failed for signal: {signal}")
                    
            except Exception as e:
                self.logger.error(f"Error executing trade: {e}")
    
    async def check_health(self):
        """Check the health status of all bot components."""
        health_status = {
            "exchange_connector": await self.exchange_connector.is_healthy(),
            "ofi_analyzer": True,  # Always healthy for now
            "signal_generator": True,  # Always healthy for now
            "risk_manager": True,  # Always healthy for now
            "overall": True
        }
        
        # Update overall health
        health_status["overall"] = all(
            health_status[key] for key in health_status if key != "overall"
        )
        
        return health_status
    
    async def log_performance_metrics(self):
        """Log current performance metrics."""
        try:
            # Get portfolio status
            portfolio = await self.exchange_connector.get_portfolio()
            
            # Get recent trades
            trades = await self.exchange_connector.get_recent_trades()
            
            # Calculate metrics
            total_pnl = sum(trade.get("pnl", 0) for trade in trades)
            win_rate = len([t for t in trades if t.get("pnl", 0) > 0]) / len(trades) if trades else 0
            
            self.logger.info(f"Performance - PnL: {total_pnl:.2f} USDT, Win Rate: {win_rate:.2%}")
            
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {e}")
    
    async def check_risk_limits(self):
        """Check if any risk limits have been exceeded."""
        try:
            # Check portfolio drawdown
            portfolio = await self.exchange_connector.get_portfolio()
            current_drawdown = portfolio.get("drawdown", 0)
            max_drawdown = self.config.get("risk_management.max_drawdown", 0.15)
            
            if current_drawdown > max_drawdown:
                self.logger.warning(f"Maximum drawdown exceeded: {current_drawdown:.2%} > {max_drawdown:.2%}")
                # Could implement automatic stop trading here
            
            # Check daily loss
            daily_loss = portfolio.get("daily_loss", 0)
            max_daily_loss = self.config.get("risk_management.max_daily_loss", 0.05)
            
            if daily_loss > max_daily_loss:
                self.logger.warning(f"Maximum daily loss exceeded: {daily_loss:.2%} > {max_daily_loss:.2%}")
                
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")


async def main():
    """Main function to run the trading bot."""
    bot = TradingBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\nReceived shutdown signal, stopping bot...")
        asyncio.create_task(bot.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start the bot
        await bot.initialize()
        await bot.start()
        
        # Keep the bot running
        while bot.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        # Ensure clean shutdown
        await bot.stop()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
