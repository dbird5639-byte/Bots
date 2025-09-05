"""
Prize Picks Bot - Main Class

This is the main trading bot class for Prize Picks sports betting,
including data analysis, betting strategies, and automated execution.
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
import numpy as np

from .config_manager import ConfigManager
from .logger import Logger
from .prize_picks_connector import PrizePicksConnector
from .data_analyzer import DataAnalyzer
from .betting_strategy import BettingStrategy
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager


class PrizePicksBot:
    """
    Main Prize Picks Bot class
    
    This class orchestrates all sports betting components including:
    - Data analysis and statistical modeling
    - Betting strategy generation and execution
    - Risk management and portfolio optimization
    - Automated bet placement and monitoring
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Prize Picks Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Prize Picks components
        self.prize_picks_connector: Optional[PrizePicksConnector] = None
        self.data_analyzer: Optional[DataAnalyzer] = None
        self.betting_strategy: Optional[BettingStrategy] = None
        self.risk_manager: Optional[RiskManager] = None
        self.portfolio_manager: Optional[PortfolioManager] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.bet_history = []
        self.account_balance = Decimal('0')
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("Prize Picks Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            self.log.info("Initializing Prize Picks Bot...")
            
            # Initialize Prize Picks connection
            self.prize_picks_connector = PrizePicksConnector(self.config, self.logger)
            await self.prize_picks_connector.initialize()
            
            # Initialize betting components
            self.data_analyzer = DataAnalyzer(self.config, self.logger)
            self.betting_strategy = BettingStrategy(self.config, self.logger, self.prize_picks_connector)
            self.risk_manager = RiskManager(self.config, self.logger)
            self.portfolio_manager = PortfolioManager(self.config, self.logger)
            
            # Initialize each component
            await self.data_analyzer.initialize()
            await self.betting_strategy.initialize()
            await self.risk_manager.initialize()
            await self.portfolio_manager.initialize()
            
            # Check account balance
            await self._check_account_balance()
            
            self.is_initialized = True
            self.log.info("Prize Picks Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Prize Picks Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the betting bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting Prize Picks Bot...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start main betting loop
            await self._betting_loop()
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to start betting bot: {e}")
            return False
    
    async def stop(self):
        """Stop the betting bot gracefully"""
        try:
            self.log.info("Stopping Prize Picks Bot...")
            self.is_running = False
            
            # Stop all components
            if self.betting_strategy:
                await self.betting_strategy.shutdown()
            if self.data_analyzer:
                await self.data_analyzer.shutdown()
            if self.prize_picks_connector:
                await self.prize_picks_connector.shutdown()
            if self.risk_manager:
                await self.risk_manager.shutdown()
            if self.portfolio_manager:
                await self.portfolio_manager.shutdown()
            
            self.log.info("Prize Picks Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _betting_loop(self):
        """Main betting loop for Prize Picks strategies"""
        try:
            while self.is_running:
                # Get available contests and props
                contests = await self.prize_picks_connector.get_available_contests()
                
                # Analyze data for each contest
                for contest in contests:
                    await self._analyze_contest(contest)
                
                # Execute betting strategies
                await self._execute_betting_strategies()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Risk management check
                await self._risk_management_check()
                
                # Check account balance
                await self._check_account_balance()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('betting.update_interval', 300))
                
        except Exception as e:
            self.log.error(f"Error in betting loop: {e}")
            await self.stop()
    
    async def _analyze_contest(self, contest: Dict[str, Any]):
        """Analyze a specific contest for betting opportunities"""
        try:
            # Get contest details and props
            contest_details = await self.prize_picks_connector.get_contest_details(contest['id'])
            
            # Analyze historical data and trends
            analysis = await self.data_analyzer.analyze_contest(contest_details)
            
            # Store analysis for strategy execution
            contest['analysis'] = analysis
            
        except Exception as e:
            self.log.error(f"Error analyzing contest {contest['id']}: {e}")
    
    async def _execute_betting_strategies(self):
        """Execute betting strategies based on analysis"""
        try:
            if self.betting_strategy and self.betting_strategy.is_enabled():
                # Get betting opportunities
                opportunities = await self.betting_strategy.find_opportunities()
                
                for opportunity in opportunities:
                    if await self.risk_manager.validate_betting_opportunity(opportunity):
                        # Execute the bet
                        bet_result = await self.betting_strategy.execute_bet(opportunity)
                        
                        if bet_result['success']:
                            # Log the successful bet
                            self.bet_history.append({
                                'timestamp': datetime.now(),
                                'type': 'bet',
                                'opportunity': opportunity,
                                'bet_result': bet_result,
                                'status': 'placed'
                            })
                            
                            self.log.info(f"Bet placed successfully: {opportunity['prop_id']}")
                        else:
                            self.log.warning(f"Bet placement failed: {opportunity['prop_id']}")
                    else:
                        self.log.warning(f"Risk manager rejected bet: {opportunity['prop_id']}")
                        
        except Exception as e:
            self.log.error(f"Error executing betting strategies: {e}")
    
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
            self.performance_metrics['account_balance'] = float(self.account_balance)
            
            # Log performance
            self.log.info(f"Performance metrics updated: {self.performance_metrics}")
            
        except Exception as e:
            self.log.error(f"Error updating performance metrics: {e}")
    
    async def _get_portfolio_performance(self) -> Dict[str, Any]:
        """Get current portfolio performance"""
        try:
            # Get active bets and results
            active_bets = await self.prize_picks_connector.get_active_bets()
            bet_results = await self.prize_picks_connector.get_bet_results()
            
            # Calculate performance metrics
            total_bets = len(self.bet_history)
            winning_bets = len([b for b in bet_results if b['result'] == 'win'])
            losing_bets = len([b for b in bet_results if b['result'] == 'loss'])
            
            win_rate = winning_bets / total_bets if total_bets > 0 else 0
            total_profit = sum([b['profit'] for b in bet_results if 'profit' in b])
            
            return {
                'total_bets': total_bets,
                'winning_bets': winning_bets,
                'losing_bets': losing_bets,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'active_bets': len(active_bets),
                'account_balance': float(self.account_balance)
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
            # Reduce bet sizes
            await self._reduce_bet_sizes()
            
            # Stop placing new bets
            await self._pause_betting()
            
            # Notify administrators
            await self._send_risk_alert()
            
        except Exception as e:
            self.log.error(f"Error taking protective measures: {e}")
    
    async def _reduce_bet_sizes(self):
        """Reduce bet sizes to manage risk"""
        # TODO: Implement bet size reduction logic
        self.log.info("Reducing bet sizes for risk management")
    
    async def _pause_betting(self):
        """Pause betting temporarily"""
        # TODO: Implement betting pause logic
        self.log.info("Pausing betting due to high risk")
    
    async def _send_risk_alert(self):
        """Send risk alert notifications"""
        # TODO: Implement alert system
        self.log.warning("RISK ALERT: High risk conditions detected")
    
    async def _check_account_balance(self):
        """Check current account balance"""
        try:
            self.account_balance = await self.prize_picks_connector.get_account_balance()
            self.log.info(f"Current account balance: ${self.account_balance}")
            
        except Exception as e:
            self.log.error(f"Error checking account balance: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_bets': len(self.bet_history),
            'account_balance': float(self.account_balance),
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
    """Main function to run the Prize Picks Bot"""
    config_path = "config/config.yaml"
    
    async with PrizePicksBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
