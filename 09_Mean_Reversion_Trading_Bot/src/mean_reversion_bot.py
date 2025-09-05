"""
Mean Reversion Trading Bot - Main Class

This is the main trading bot class for Mean Reversion Trading,
implementing statistical mean reversion strategies across various asset classes.
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
from scipy import stats

from .config_manager import ConfigManager
from .logger import Logger
from .data_manager import DataManager
from .mean_reversion_strategy import MeanReversionStrategy
from .statistical_analyzer import StatisticalAnalyzer
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager


class MeanReversionTradingBot:
    """
    Main Mean Reversion Trading Bot class
    
    This class orchestrates mean reversion trading strategies including:
    - Bollinger Bands mean reversion
    - RSI divergence strategies
    - Moving average crossovers
    - Statistical arbitrage
    - Mean reversion across multiple timeframes
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Mean Reversion Trading Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Core components
        self.data_manager: Optional[DataManager] = None
        self.mean_reversion_strategy: Optional[MeanReversionStrategy] = None
        self.statistical_analyzer: Optional[StatisticalAnalyzer] = None
        self.risk_manager: Optional[RiskManager] = None
        self.portfolio_manager: Optional[PortfolioManager] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.trade_history = []
        self.strategy_performance = {}
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("Mean Reversion Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            self.log.info("Initializing Mean Reversion Trading Bot...")
            
            # Initialize core components
            self.data_manager = DataManager(self.config, self.logger)
            self.mean_reversion_strategy = MeanReversionStrategy(self.config, self.logger)
            self.statistical_analyzer = StatisticalAnalyzer(self.config, self.logger)
            self.risk_manager = RiskManager(self.config, self.logger)
            self.portfolio_manager = PortfolioManager(self.config, self.logger)
            
            # Initialize each component
            await self.data_manager.initialize()
            await self.mean_reversion_strategy.initialize()
            await self.statistical_analyzer.initialize()
            await self.risk_manager.initialize()
            await self.portfolio_manager.initialize()
            
            self.is_initialized = True
            self.log.info("Mean Reversion Trading Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize Mean Reversion Trading Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the trading bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting Mean Reversion Trading Bot...")
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
            self.log.info("Stopping Mean Reversion Trading Bot...")
            self.is_running = False
            
            # Stop all components
            if self.mean_reversion_strategy:
                await self.mean_reversion_strategy.shutdown()
            if self.data_manager:
                await self.data_manager.shutdown()
            if self.statistical_analyzer:
                await self.statistical_analyzer.shutdown()
            if self.risk_manager:
                await self.risk_manager.shutdown()
            if self.portfolio_manager:
                await self.portfolio_manager.shutdown()
            
            self.log.info("Mean Reversion Trading Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _trading_loop(self):
        """Main trading loop for mean reversion strategies"""
        try:
            while self.is_running:
                # Get market data for all configured assets
                market_data = await self.data_manager.get_market_data()
                
                # Analyze mean reversion opportunities
                opportunities = await self._analyze_mean_reversion_opportunities(market_data)
                
                # Execute mean reversion strategies
                await self._execute_mean_reversion_strategies(opportunities)
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Risk management check
                await self._risk_management_check()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('trading.update_interval', 60))
                
        except Exception as e:
            self.log.error(f"Error in trading loop: {e}")
            await self.stop()
    
    async def _analyze_mean_reversion_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze market data for mean reversion opportunities"""
        try:
            opportunities = []
            
            for asset, data in market_data.items():
                # Analyze each asset for mean reversion signals
                asset_opportunities = await self._analyze_asset_mean_reversion(asset, data)
                opportunities.extend(asset_opportunities)
            
            self.log.info(f"Found {len(opportunities)} mean reversion opportunities")
            return opportunities
            
        except Exception as e:
            self.log.error(f"Error analyzing mean reversion opportunities: {e}")
            return []
    
    async def _analyze_asset_mean_reversion(self, asset: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a specific asset for mean reversion opportunities"""
        try:
            opportunities = []
            
            # Get historical price data
            price_data = data.get('price_data', pd.DataFrame())
            if price_data.empty:
                return opportunities
            
            # Calculate mean reversion indicators
            bollinger_signals = await self._calculate_bollinger_signals(price_data)
            rsi_signals = await self._calculate_rsi_signals(price_data)
            ma_signals = await self._calculate_moving_average_signals(price_data)
            statistical_signals = await self._calculate_statistical_signals(price_data)
            
            # Combine signals and create opportunities
            if bollinger_signals:
                opportunities.append({
                    'asset': asset,
                    'strategy': 'bollinger_bands',
                    'signal': bollinger_signals,
                    'confidence': bollinger_signals.get('confidence', 0.0),
                    'timestamp': datetime.now()
                })
            
            if rsi_signals:
                opportunities.append({
                    'asset': asset,
                    'strategy': 'rsi_divergence',
                    'signal': rsi_signals,
                    'confidence': rsi_signals.get('confidence', 0.0),
                    'timestamp': datetime.now()
                })
            
            if ma_signals:
                opportunities.append({
                    'asset': asset,
                    'strategy': 'moving_average_crossover',
                    'signal': ma_signals,
                    'confidence': ma_signals.get('confidence', 0.0),
                    'timestamp': datetime.now()
                })
            
            if statistical_signals:
                opportunities.append({
                    'asset': asset,
                    'strategy': 'statistical_arbitrage',
                    'signal': statistical_signals,
                    'confidence': statistical_signals.get('confidence', 0.0),
                    'timestamp': datetime.now()
                })
            
            return opportunities
            
        except Exception as e:
            self.log.error(f"Error analyzing asset {asset} for mean reversion: {e}")
            return []
    
    async def _calculate_bollinger_signals(self, price_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate Bollinger Bands mean reversion signals"""
        try:
            if len(price_data) < 20:
                return None
            
            # Calculate Bollinger Bands
            close_prices = price_data['close']
            sma_20 = close_prices.rolling(window=20).mean()
            std_20 = close_prices.rolling(window=20).std()
            
            upper_band = sma_20 + (2 * std_20)
            lower_band = sma_20 - (2 * std_20)
            
            current_price = close_prices.iloc[-1]
            current_sma = sma_20.iloc[-1]
            
            # Generate signals
            if current_price <= lower_band.iloc[-1]:
                # Price below lower band - potential buy signal
                signal = 'buy'
                confidence = min(0.9, (lower_band.iloc[-1] - current_price) / current_price * 10)
            elif current_price >= upper_band.iloc[-1]:
                # Price above upper band - potential sell signal
                signal = 'sell'
                confidence = min(0.9, (current_price - upper_band.iloc[-1]) / current_price * 10)
            else:
                # Price within bands - no signal
                return None
            
            return {
                'signal': signal,
                'confidence': confidence,
                'current_price': current_price,
                'sma_20': current_sma,
                'upper_band': upper_band.iloc[-1],
                'lower_band': lower_band.iloc[-1],
                'bandwidth': (upper_band.iloc[-1] - lower_band.iloc[-1]) / current_sma
            }
            
        except Exception as e:
            self.log.error(f"Error calculating Bollinger signals: {e}")
            return None
    
    async def _calculate_rsi_signals(self, price_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate RSI divergence mean reversion signals"""
        try:
            if len(price_data) < 14:
                return None
            
            # Calculate RSI
            close_prices = price_data['close']
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Generate signals based on RSI extremes
            if current_rsi <= 30:
                # Oversold - potential buy signal
                signal = 'buy'
                confidence = min(0.9, (30 - current_rsi) / 30)
            elif current_rsi >= 70:
                # Overbought - potential sell signal
                signal = 'sell'
                confidence = min(0.9, (current_rsi - 70) / 30)
            else:
                # Neutral - no signal
                return None
            
            return {
                'signal': signal,
                'confidence': confidence,
                'current_rsi': current_rsi,
                'rsi_trend': 'oversold' if current_rsi <= 30 else 'overbought'
            }
            
        except Exception as e:
            self.log.error(f"Error calculating RSI signals: {e}")
            return None
    
    async def _calculate_moving_average_signals(self, price_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate moving average crossover mean reversion signals"""
        try:
            if len(price_data) < 50:
                return None
            
            # Calculate moving averages
            close_prices = price_data['close']
            ma_20 = close_prices.rolling(window=20).mean()
            ma_50 = close_prices.rolling(window=50).mean()
            
            current_price = close_prices.iloc[-1]
            current_ma_20 = ma_20.iloc[-1]
            current_ma_50 = ma_50.iloc[-1]
            
            # Previous values for crossover detection
            prev_ma_20 = ma_20.iloc[-2]
            prev_ma_50 = ma_50.iloc[-2]
            
            # Check for crossovers
            if prev_ma_20 <= prev_ma_50 and current_ma_20 > current_ma_50:
                # Golden cross - potential buy signal
                signal = 'buy'
                confidence = 0.7
            elif prev_ma_20 >= prev_ma_50 and current_ma_20 < current_ma_50:
                # Death cross - potential sell signal
                signal = 'sell'
                confidence = 0.7
            else:
                # No crossover - no signal
                return None
            
            return {
                'signal': signal,
                'confidence': confidence,
                'current_price': current_price,
                'ma_20': current_ma_20,
                'ma_50': current_ma_50,
                'crossover_type': 'golden' if signal == 'buy' else 'death'
            }
            
        except Exception as e:
            self.log.error(f"Error calculating moving average signals: {e}")
            return None
    
    async def _calculate_statistical_signals(self, price_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate statistical mean reversion signals"""
        try:
            if len(price_data) < 100:
                return None
            
            # Calculate returns
            close_prices = price_data['close']
            returns = close_prices.pct_change().dropna()
            
            if len(returns) < 50:
                return None
            
            # Calculate z-score of current return
            mean_return = returns.mean()
            std_return = returns.std()
            current_return = returns.iloc[-1]
            z_score = (current_return - mean_return) / std_return
            
            # Generate signals based on z-score
            if abs(z_score) > 2.0:
                if z_score > 2.0:
                    # High positive return - potential sell signal (mean reversion)
                    signal = 'sell'
                    confidence = min(0.9, abs(z_score) / 4.0)
                else:
                    # High negative return - potential buy signal (mean reversion)
                    signal = 'buy'
                    confidence = min(0.9, abs(z_score) / 4.0)
                
                return {
                    'signal': signal,
                    'confidence': confidence,
                    'z_score': z_score,
                    'current_return': current_return,
                    'mean_return': mean_return,
                    'std_return': std_return
                }
            
            return None
            
        except Exception as e:
            self.log.error(f"Error calculating statistical signals: {e}")
            return None
    
    async def _execute_mean_reversion_strategies(self, opportunities: List[Dict[str, Any]]):
        """Execute mean reversion strategies based on opportunities"""
        try:
            if not opportunities:
                return
            
            # Sort opportunities by confidence
            sorted_opportunities = sorted(opportunities, key=lambda x: x['confidence'], reverse=True)
            
            for opportunity in sorted_opportunities[:5]:  # Limit to top 5 opportunities
                if await self.risk_manager.validate_opportunity(opportunity):
                    # Execute the strategy
                    execution_result = await self.mean_reversion_strategy.execute_strategy(opportunity)
                    
                    if execution_result['success']:
                        # Log the successful trade
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'mean_reversion',
                            'opportunity': opportunity,
                            'execution_result': execution_result,
                            'status': 'executed'
                        })
                        
                        self.log.info(f"Executed mean reversion strategy: {opportunity['asset']} - {opportunity['strategy']}")
                    else:
                        self.log.warning(f"Strategy execution failed: {opportunity['asset']} - {opportunity['strategy']}")
                else:
                    self.log.warning(f"Risk manager rejected opportunity: {opportunity['asset']} - {opportunity['strategy']}")
                    
        except Exception as e:
            self.log.error(f"Error executing mean reversion strategies: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get current portfolio performance
            portfolio_performance = await self.portfolio_manager.get_performance_metrics()
            
            # Update metrics
            self.performance_metrics.update(portfolio_performance)
            self.performance_metrics['uptime'] = (
                datetime.now() - self.start_time
            ).total_seconds() if self.start_time else 0
            self.performance_metrics['total_trades'] = len(self.trade_history)
            
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_trades': len(self.trade_history),
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
    """Main function to run the Mean Reversion Trading Bot"""
    config_path = "config/config.yaml"
    
    async with MeanReversionTradingBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
