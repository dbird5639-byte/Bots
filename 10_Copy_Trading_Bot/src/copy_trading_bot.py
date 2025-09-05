"""
Copy Trading Bot - Main Class

This is the main trading bot class for Copy Trading,
implementing automated systems that mirror successful traders' strategies.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import signal
import sys
from decimal import Decimal

import pandas as pd
import numpy as np

from .config_manager import ConfigManager
from .logger import Logger
from .trader_analyzer import TraderAnalyzer
from .copy_executor import CopyExecutor
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager
from .performance_tracker import PerformanceTracker


class CopyTradingBot:
    """
    Main Copy Trading Bot class
    
    This class orchestrates copy trading operations including:
    - Trader selection and analysis
    - Trade copying and execution
    - Risk management and position sizing
    - Portfolio optimization and rebalancing
    - Performance tracking and analytics
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Copy Trading Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Core components
        self.trader_analyzer: Optional[TraderAnalyzer] = None
        self.copy_executor: Optional[CopyExecutor] = None
        self.risk_manager: Optional[RiskManager] = None
        self.portfolio_manager: Optional[PortfolioManager] = None
        self.performance_tracker: Optional[PerformanceTracker] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.copy_trade_history = []
        self.trader_performance = {}
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("Copy Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            self.log.info("Initializing Copy Trading Bot...")
            
            # Initialize core components
            self.trader_analyzer = TraderAnalyzer(self.config, self.logger)
            self.copy_executor = CopyExecutor(self.config, self.logger)
            self.risk_manager = RiskManager(self.config, self.logger)
            self.portfolio_manager = PortfolioManager(self.config, self.logger)
            self.performance_tracker = PerformanceTracker(self.config, self.logger)
            
            # Initialize each component
            await self.trader_analyzer.initialize()
            await self.copy_executor.initialize()
            await self.risk_manager.initialize()
            await self.portfolio_manager.initialize()
            await self.performance_tracker.initialize()
            
            self.is_initialized = True
            self.log.info("Copy Trading Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Copy Trading Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the copy trading bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting Copy Trading Bot...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start main copy trading loop
            await self._copy_trading_loop()
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to start copy trading bot: {e}")
            return False
    
    async def stop(self):
        """Stop the copy trading bot gracefully"""
        try:
            self.log.info("Stopping Copy Trading Bot...")
            self.is_running = False
            
            # Stop all components
            if self.trader_analyzer:
                await self.trader_analyzer.shutdown()
            if self.copy_executor:
                await self.copy_executor.shutdown()
            if self.risk_manager:
                await self.risk_manager.shutdown()
            if self.portfolio_manager:
                await self.portfolio_manager.shutdown()
            if self.performance_tracker:
                await self.performance_tracker.shutdown()
            
            self.log.info("Copy Trading Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _copy_trading_loop(self):
        """Main copy trading loop"""
        try:
            while self.is_running:
                # Phase 1: Analyze and select traders
                await self._execute_trader_analysis_phase()
                
                # Phase 2: Monitor trader activities
                await self._execute_trader_monitoring_phase()
                
                # Phase 3: Execute copy trades
                await self._execute_copy_trading_phase()
                
                # Phase 4: Portfolio optimization
                await self._execute_portfolio_optimization_phase()
                
                # Phase 5: Performance tracking
                await self._execute_performance_tracking_phase()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Risk management check
                await self._risk_management_check()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('copy_trading.update_interval', 300))
                
        except Exception as e:
            self.log.error(f"Error in copy trading loop: {e}")
            await self.stop()
    
    async def _execute_trader_analysis_phase(self):
        """Execute trader analysis and selection phase"""
        try:
            self.log.info("Executing Trader Analysis Phase...")
            
            # Analyze available traders
            available_traders = await self.trader_analyzer.get_available_traders()
            
            # Filter and rank traders based on performance
            qualified_traders = await self.trader_analyzer.filter_qualified_traders(available_traders)
            
            # Select top traders for copying
            selected_traders = await self.trader_analyzer.select_top_traders(qualified_traders)
            
            # Store selected traders
            await self.trader_analyzer.update_selected_traders(selected_traders)
            
            self.log.info(f"Trader Analysis Phase completed: {len(selected_traders)} traders selected")
            
        except Exception as e:
            self.log.error(f"Error in trader analysis phase: {e}")
    
    async def _execute_trader_monitoring_phase(self):
        """Execute trader monitoring phase"""
        try:
            self.log.info("Executing Trader Monitoring Phase...")
            
            # Get selected traders
            selected_traders = await self.trader_analyzer.get_selected_traders()
            
            # Monitor each trader's activities
            for trader in selected_traders:
                trader_activities = await self.trader_analyzer.monitor_trader_activities(trader)
                
                if trader_activities:
                    # Store trader activities for copy execution
                    await self.copy_executor.store_trader_activities(trader['id'], trader_activities)
            
            self.log.info("Trader Monitoring Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in trader monitoring phase: {e}")
    
    async def _execute_copy_trading_phase(self):
        """Execute copy trading phase"""
        try:
            self.log.info("Executing Copy Trading Phase...")
            
            # Get stored trader activities
            trader_activities = await self.copy_executor.get_stored_trader_activities()
            
            for trader_id, activities in trader_activities.items():
                for activity in activities:
                    # Validate copy trade opportunity
                    if await self.risk_manager.validate_copy_trade(activity):
                        # Execute copy trade
                        copy_result = await self.copy_executor.execute_copy_trade(activity)
                        
                        if copy_result['success']:
                            # Log the successful copy trade
                            self.copy_trade_history.append({
                                'timestamp': datetime.now(),
                                'type': 'copy_trade',
                                'trader_id': trader_id,
                                'activity': activity,
                                'copy_result': copy_result,
                                'status': 'executed'
                            })
                            
                            self.log.info(f"Copy trade executed: Trader {trader_id} - {activity['type']}")
                        else:
                            self.log.warning(f"Copy trade failed: Trader {trader_id} - {activity['type']}")
                    else:
                        self.log.warning(f"Risk manager rejected copy trade: Trader {trader_id} - {activity['type']}")
            
            # Clear processed activities
            await self.copy_executor.clear_processed_activities()
            
            self.log.info("Copy Trading Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in copy trading phase: {e}")
    
    async def _execute_portfolio_optimization_phase(self):
        """Execute portfolio optimization phase"""
        try:
            self.log.info("Executing Portfolio Optimization Phase...")
            
            # Get current portfolio state
            portfolio_state = await self.portfolio_manager.get_portfolio_state()
            
            # Get copy trading performance
            copy_performance = await self.performance_tracker.get_copy_trading_performance()
            
            # Optimize portfolio based on copy trading results
            optimization_recommendations = await self.portfolio_manager.optimize_portfolio(
                portfolio_state, copy_performance
            )
            
            # Execute optimization recommendations
            if optimization_recommendations:
                await self.portfolio_manager.execute_optimization(optimization_recommendations)
            
            self.log.info("Portfolio Optimization Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in portfolio optimization phase: {e}")
    
    async def _execute_performance_tracking_phase(self):
        """Execute performance tracking phase"""
        try:
            self.log.info("Executing Performance Tracking Phase...")
            
            # Track copy trading performance
            copy_performance = await self.performance_tracker.track_copy_trading_performance()
            
            # Track individual trader performance
            trader_performance = await self.performance_tracker.track_trader_performance()
            
            # Update performance metrics
            self.trader_performance.update(trader_performance)
            
            # Log performance
            self.log.info(f"Copy Trading Performance: {copy_performance}")
            self.log.info(f"Trader Performance: {trader_performance}")
            
            self.log.info("Performance Tracking Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in performance tracking phase: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get current portfolio performance
            portfolio_performance = await self.portfolio_manager.get_performance_metrics()
            
            # Get copy trading performance
            copy_performance = await self.performance_tracker.get_copy_trading_performance()
            
            # Update metrics
            self.performance_metrics.update(portfolio_performance)
            self.performance_metrics.update(copy_performance)
            self.performance_metrics['uptime'] = (
                datetime.now() - self.start_time
            ).total_seconds() if self.start_time else 0
            self.performance_metrics['total_copy_trades'] = len(self.copy_trade_history)
            self.performance_metrics['active_traders'] = len(self.trader_performance)
            
            # Log performance
            self.log.info(f"Performance metrics updated: {self.performance_metrics}")
            
        except Exception as e:
            self.log.error(f"Error updating performance metrics: {e}")
    
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
            # Reduce copy trade sizes
            await self._reduce_copy_trade_sizes()
            
            # Stop copying high-risk traders
            await self._pause_high_risk_traders()
            
            # Notify administrators
            await self._send_risk_alert()
            
        except Exception as e:
            self.log.error(f"Error taking protective measures: {e}")
    
    async def _reduce_copy_trade_sizes(self):
        """Reduce copy trade sizes to manage risk"""
        # TODO: Implement copy trade size reduction logic
        self.log.info("Reducing copy trade sizes for risk management")
    
    async def _pause_high_risk_traders(self):
        """Pause copying high-risk traders"""
        # TODO: Implement trader pausing logic
        self.log.info("Pausing high-risk traders due to risk management")
    
    async def _send_risk_alert(self):
        """Send risk alert notifications"""
        # TODO: Implement alert system
        self.log.warning("RISK ALERT: High risk conditions detected")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_copy_trades': len(self.copy_trade_history),
            'active_traders': len(self.trader_performance),
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
    """Main function to run the Copy Trading Bot"""
    config_path = "config/config.yaml"
    
    async with CopyTradingBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
