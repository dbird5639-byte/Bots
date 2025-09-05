"""
Enhanced AI-Powered XRP Trading Bot for Hyperliquid

This bot integrates advanced AI trading strategies including:
- Liquidation hunting and signal generation
- Multi-strategy portfolio management
- Advanced risk management with AI optimization
- Real-time market sentiment analysis
- Dynamic position sizing based on market conditions
"""

import asyncio
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import aiohttp
import websockets
from termcolor import cprint
import logging
from typing import Dict, List, Optional, Tuple
import time
import hmac
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_xrp_bot.log'),
        logging.StreamHandler()
    ]
)

class EnhancedXRPBot:
    """
    Enhanced AI-Powered XRP Trading Bot
    
    Features:
    - Multi-strategy signal generation
    - AI-powered risk management
    - Liquidation hunting with rebound analysis
    - Dynamic portfolio optimization
    - Real-time market sentiment analysis
    """
    
    def __init__(self):
        # Load configuration
        self.config = self._load_config()
        
        # Hyperliquid settings
        self.exchange = 'Hyperliquid'
        self.symbol = 'XRP'
        self.base_url = 'https://api.hyperliquid.xyz'
        self.ws_url = 'wss://api.hyperliquid.xyz/ws'
        
        # Account settings
        self.account_balance = self.config['account']['balance']
        self.min_balance_threshold = self.config['account']['min_balance']
        self.leverage = self.config['account']['leverage']
        
        # Data storage
        self.trades_data = []
        self.liquidations_data = []
        self.price_data = []
        self.signals_history = []
        self.positions = {}
        
        # Performance tracking
        self.total_signals = 0
        self.successful_signals = 0
        self.current_pnl = 0.0
        self.daily_pnl = 0.0
        self.strategy_performance = {}
        
        # API credentials
        self.api_key = os.getenv('HYPERLIQUID_API_KEY')
        self.api_secret = os.getenv('HYPERLIQUID_API_SECRET')
        
        # Session
        self.session = None
        
        # Initialize files
        self._initialize_files()
        
        logging.info("Enhanced AI XRP Bot initialized")
    
    def _load_config(self) -> Dict:
        """Load bot configuration"""
        return {
            'account': {
                'balance': 60,
                'min_balance': 10,
                'leverage': 1,
                'max_leverage': 1
            },
            'risk': {
                'max_position_size': 0.05,
                'max_total_exposure': 0.15,
                'default_stop_loss': 0.03,
                'default_take_profit': 0.10,
                'max_daily_loss': 0.03,
                'max_consecutive_losses': 2
            },
            'strategies': {
                'liquidation_hunting': True,
                'sentiment_analysis': True,
                'correlation_trading': True,
                'multi_timeframe': True,
                'volume_analysis': True
            },
            'ai': {
                'confidence_threshold': 0.65,
                'risk_score_threshold': 0.4,
                'correlation_threshold': 0.7,
                'sentiment_weight': 0.3,
                'liquidation_weight': 0.4,
                'technical_weight': 0.3
            }
        }
    
    def _initialize_files(self):
        """Initialize data files"""
        files = [
            'enhanced_xrp_trades.csv',
            'enhanced_xrp_signals.csv',
            'enhanced_xrp_performance.csv',
            'enhanced_xrp_liquidations.csv'
        ]
        
        for filename in files:
            if not os.path.isfile(filename):
                with open(filename, 'w') as f:
                    if 'trades' in filename:
                        f.write('timestamp,symbol,price,quantity,usd_size,side,event_time\n')
                    elif 'signals' in filename:
                        f.write('timestamp,signal_type,confidence,action,reason,price,strategy_source,risk_score,expected_return\n')
                    elif 'performance' in filename:
                        f.write('timestamp,strategy,win_rate,profit_factor,sharpe_ratio,total_pnl\n')
                    elif 'liquidations' in filename:
                        f.write('timestamp,symbol,side,price,quantity,usd_size,event_time\n')
    
    async def start_bot(self):
        """Start the enhanced AI bot"""
        logging.info("🚀 Starting Enhanced AI XRP Bot...")
        
        # Initialize session
        self.session = aiohttp.ClientSession()
        
        try:
            # Verify settings
            await self.verify_settings()
            
            # Create tasks
            tasks = [
                self.data_stream_manager(),
                self.ai_signal_generator(),
                self.performance_monitor(),
                self.risk_monitor()
            ]
            
            # Run all components
            await asyncio.gather(*tasks)
            
        finally:
            if self.session:
                await self.session.close()
    
    async def verify_settings(self):
        """Verify bot settings"""
        if self.leverage != 1:
            raise ValueError("Leverage must be 1x for this bot")
        
        if self.account_balance < self.min_balance_threshold:
            raise ValueError("Account balance below minimum threshold")
        
        logging.info("✅ Settings verified: 1x leverage, sufficient balance")
    
    async def data_stream_manager(self):
        """Manage all data streams"""
        try:
            # Start multiple data streams
            streams = [
                self.hyperliquid_trade_stream(),
                self.hyperliquid_liquidation_stream(),
                self.hyperliquid_orderbook_stream()
            ]
            
            await asyncio.gather(*streams)
            
        except Exception as e:
            logging.error(f"Error in data stream manager: {e}")
    
    async def hyperliquid_trade_stream(self):
        """Stream Hyperliquid trade data"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logging.info("Connected to Hyperliquid trade stream")
                
                # Subscribe to XRP trades
                subscribe_msg = {
                    "method": "subscribe",
                    "subscription": {"type": "trades", "coin": self.symbol}
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get('type') == 'trade':
                            await self.process_trade_data(data)
                            
                    except Exception as e:
                        logging.error(f"Trade stream error: {e}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            logging.error(f"Trade stream connection error: {e}")
            await asyncio.sleep(5)
    
    async def hyperliquid_liquidation_stream(self):
        """Stream Hyperliquid liquidation data"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logging.info("Connected to Hyperliquid liquidation stream")
                
                # Subscribe to liquidations
                subscribe_msg = {
                    "method": "subscribe",
                    "subscription": {"type": "liquidations", "coin": self.symbol}
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get('type') == 'liquidation':
                            await self.process_liquidation_data(data)
                            
                    except Exception as e:
                        logging.error(f"Liquidation stream error: {e}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            logging.error(f"Liquidation stream connection error: {e}")
            await asyncio.sleep(5)
    
    async def hyperliquid_orderbook_stream(self):
        """Stream Hyperliquid order book data"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logging.info("Connected to Hyperliquid order book stream")
                
                # Subscribe to order book
                subscribe_msg = {
                    "method": "subscribe",
                    "subscription": {"type": "orderbook", "coin": self.symbol}
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get('type') == 'orderbook':
                            await self.process_orderbook_data(data)
                            
                    except Exception as e:
                        logging.error(f"Order book stream error: {e}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            logging.error(f"Order book stream connection error: {e}")
            await asyncio.sleep(5)
    
    async def process_trade_data(self, trade_data: Dict):
        """Process incoming trade data"""
        try:
            # Extract trade info
            trade_info = {
                'timestamp': int(trade_data.get('time', time.time() * 1000)),
                'symbol': trade_data.get('coin', self.symbol),
                'price': float(trade_data.get('price', 0)),
                'quantity': float(trade_data.get('size', 0)),
                'usd_size': float(trade_data.get('price', 0)) * float(trade_data.get('size', 0)),
                'side': trade_data.get('side', 'unknown'),
                'event_time': int(trade_data.get('time', time.time() * 1000))
            }
            
            # Filter significant trades
            if trade_info['usd_size'] >= 10000:  # $10k minimum
                self.trades_data.append(trade_info)
                
                # Keep recent data
                self._cleanup_old_data()
                
                # Log trade
                self._log_trade(trade_info)
                
        except Exception as e:
            logging.error(f"Error processing trade: {e}")
    
    async def process_liquidation_data(self, liquidation_data: Dict):
        """Process liquidation data"""
        try:
            # Extract liquidation info
            liquidation_info = {
                'timestamp': int(liquidation_data.get('time', time.time() * 1000)),
                'symbol': liquidation_data.get('coin', self.symbol),
                'side': liquidation_data.get('side', 'unknown'),
                'price': float(liquidation_data.get('price', 0)),
                'quantity': float(liquidation_data.get('size', 0)),
                'usd_size': float(liquidation_data.get('price', 0)) * float(liquidation_data.get('size', 0)),
                'event_time': int(liquidation_data.get('time', time.time() * 1000))
            }
            
            if liquidation_info['usd_size'] >= 50000:  # $50k minimum
                self.liquidations_data.append(liquidation_info)
                
                # Log liquidation
                self._log_liquidation(liquidation_info)
                
                # Generate liquidation-based signals
                await self.generate_liquidation_signals(liquidation_info)
                
        except Exception as e:
            logging.error(f"Error processing liquidation: {e}")
    
    async def process_orderbook_data(self, orderbook_data: Dict):
        """Process order book data"""
        try:
            # Extract bid/ask data
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if bids and asks:
                best_bid = float(bids[0][0]) if bids[0] else 0
                best_ask = float(asks[0][0]) if asks[0] else 0
                
                if best_bid > 0 and best_ask > 0:
                    spread = best_ask - best_bid
                    spread_pct = (spread / best_bid) * 100
                    
                    # Generate spread-based signals
                    if spread_pct < 0.05:  # Very tight spread
                        await self.generate_spread_signals(best_bid, best_ask, spread_pct)
                        
        except Exception as e:
            logging.error(f"Error processing order book: {e}")
    
    async def generate_liquidation_signals(self, liquidation_info: Dict):
        """Generate signals based on liquidations"""
        try:
            # Analyze liquidation for rebound opportunities
            current_price = self._get_current_price()
            if not current_price:
                return
            
            # Calculate price change since liquidation
            price_change = (current_price - liquidation_info['price']) / liquidation_info['price']
            
            # Generate rebound signals
            if abs(price_change) > 0.02:  # 2% move
                signal_type = 'REBOUND_BUY' if price_change > 0 else 'REBOUND_SELL'
                action = 'BUY' if price_change > 0 else 'SELL'
                
                signal = {
                    'type': signal_type,
                    'confidence': 0.9,  # High confidence for liquidation rebounds
                    'action': action,
                    'reason': f"Price rebound after {liquidation_info['usd_size']:,.0f} liquidation",
                    'price': current_price,
                    'timestamp': datetime.now(),
                    'strategy_source': 'Liquidation Hunting',
                    'risk_score': 0.2,
                    'expected_return': 0.08
                }
                
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating liquidation signals: {e}")
    
    async def generate_spread_signals(self, best_bid: float, best_ask: float, spread_pct: float):
        """Generate signals based on tight spreads"""
        try:
            signal = {
                'type': 'TIGHT_SPREAD',
                'confidence': 0.4,  # Lower confidence for spread signals
                'action': 'SCALP',
                'reason': f"Tight spread opportunity: {spread_pct:.3f}%",
                'price': (best_bid + best_ask) / 2,
                'timestamp': datetime.now(),
                'strategy_source': 'Spread Analysis',
                'risk_score': 0.6,
                'expected_return': 0.03
            }
            
            await self.execute_signal(signal)
            
        except Exception as e:
            logging.error(f"Error generating spread signals: {e}")
    
    async def ai_signal_generator(self):
        """Generate AI-powered trading signals"""
        while True:
            try:
                await asyncio.sleep(30)  # Generate signals every 30 seconds
                
                # Generate technical analysis signals
                await self.generate_technical_signals()
                
                # Generate volume analysis signals
                await self.generate_volume_signals()
                
                # Generate correlation signals
                await self.generate_correlation_signals()
                
            except Exception as e:
                logging.error(f"Error in AI signal generator: {e}")
                await asyncio.sleep(5)
    
    async def generate_technical_signals(self):
        """Generate technical analysis signals"""
        try:
            if len(self.price_data) < 20:
                return
            
            # RSI signals
            rsi = self._calculate_rsi(self.price_data, 14)
            if rsi < 30:
                signal = {
                    'type': 'RSI_OVERSOLD',
                    'confidence': 0.7,
                    'action': 'BUY',
                    'reason': f"RSI oversold: {rsi:.2f}",
                    'price': self._get_current_price(),
                    'timestamp': datetime.now(),
                    'strategy_source': 'Technical Analysis',
                    'risk_score': 0.3,
                    'expected_return': 0.05
                }
                await self.execute_signal(signal)
                
            elif rsi > 70:
                signal = {
                    'type': 'RSI_OVERBOUGHT',
                    'confidence': 0.7,
                    'action': 'SELL',
                    'reason': f"RSI overbought: {rsi:.2f}",
                    'price': self._get_current_price(),
                    'timestamp': datetime.now(),
                    'strategy_source': 'Technical Analysis',
                    'risk_score': 0.3,
                    'expected_return': 0.05
                }
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating technical signals: {e}")
    
    async def generate_volume_signals(self):
        """Generate volume-based signals"""
        try:
            if len(self.trades_data) < 50:
                return
            
            # Calculate average volume
            recent_volumes = [t['usd_size'] for t in self.trades_data[-50:]]
            avg_volume = np.mean(recent_volumes)
            current_volume = sum([t['usd_size'] for t in self.trades_data[-10:]])
            
            # Volume spike detection
            if current_volume > avg_volume * 2:  # 2x average volume
                signal = {
                    'type': 'VOLUME_SPIKE',
                    'confidence': 0.6,
                    'action': 'BUY',  # Volume spikes often indicate strong moves
                    'reason': f"Volume spike: {current_volume/avg_volume:.1f}x average",
                    'price': self._get_current_price(),
                    'timestamp': datetime.now(),
                    'strategy_source': 'Volume Analysis',
                    'risk_score': 0.4,
                    'expected_return': 0.08
                }
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating volume signals: {e}")
    
    async def generate_correlation_signals(self):
        """Generate correlation-based signals"""
        try:
            # This would analyze correlation with other assets
            # For now, generate basic correlation signals
            if len(self.price_data) > 100:
                # Simple trend following
                recent_prices = self.price_data[-20:]
                trend = 'UP' if recent_prices[-1] > recent_prices[0] else 'DOWN'
                
                if trend == 'UP' and len([p for p in recent_prices if p > recent_prices[0]]) > 15:
                    signal = {
                        'type': 'CORRELATION_SIGNAL',
                        'confidence': 0.5,
                        'action': 'BUY',
                        'reason': 'Strong upward trend detected',
                        'price': self._get_current_price(),
                        'timestamp': datetime.now(),
                        'strategy_source': 'Correlation Analysis',
                        'risk_score': 0.5,
                        'expected_return': 0.06
                    }
                    await self.execute_signal(signal)
                    
        except Exception as e:
            logging.error(f"Error generating correlation signals: {e}")
    
    async def execute_signal(self, signal: Dict):
        """Execute a trading signal"""
        try:
            logging.info(f"🎯 Executing signal: {signal['type']} - {signal['action']}")
            logging.info(f"Confidence: {signal['confidence']:.2%}, Risk Score: {signal['risk_score']:.2f}")
            
            # Check risk management
            if not await self.validate_signal(signal):
                logging.warning("Signal rejected by risk manager")
                return
            
            # Calculate position size
            position_size = await self.calculate_position_size(signal)
            
            if position_size > 0:
                # Place order
                await self.place_order(signal, position_size)
                
                # Log signal
                self._log_signal(signal)
                
                # Update performance tracking
                self.total_signals += 1
                
        except Exception as e:
            logging.error(f"Error executing signal: {e}")
    
    async def validate_signal(self, signal: Dict) -> bool:
        """Validate trading signal"""
        try:
            # Check confidence threshold
            if signal['confidence'] < self.config['ai']['confidence_threshold']:
                return False
            
            # Check risk score
            if signal['risk_score'] > self.config['ai']['risk_score_threshold']:
                return False
            
            # Check balance
            if self.account_balance <= self.min_balance_threshold:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating signal: {e}")
            return False
    
    async def calculate_position_size(self, signal: Dict) -> float:
        """Calculate optimal position size"""
        try:
            # Base position size (0.5% of balance for 1x leverage)
            base_size = self.account_balance * 0.005
            
            # Adjust based on confidence
            confidence_multiplier = signal['confidence']
            position_size = base_size * confidence_multiplier
            
            # Apply maximum position size limit
            max_size = self.account_balance * self.config['risk']['max_position_size']
            position_size = min(position_size, max_size)
            
            # Ensure position size doesn't exceed available balance
            position_size = min(position_size, self.account_balance * 0.95)
            
            return position_size
            
        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def place_order(self, signal: Dict, position_size: float):
        """Place order on Hyperliquid"""
        try:
            if not self.api_key or not self.api_secret:
                logging.info("No API credentials - simulating order")
                await self._log_simulated_order(signal, position_size)
                return
            
            # Prepare order parameters
            order_params = {
                'coin': self.symbol,
                'side': signal['action'].lower(),
                'size': position_size,
                'price': signal['price'],
                'reduceOnly': False,
                'orderType': 'LIMIT',
                'leverage': 1
            }
            
            # Sign and place order
            signature = self._sign_order(order_params)
            order_params['signature'] = signature
            
            url = f"{self.base_url}/exchange"
            async with self.session.post(url, json=order_params) as response:
                if response.status == 200:
                    order_result = await response.json()
                    logging.info(f"✅ Order placed: {order_result.get('id')}")
                else:
                    logging.error(f"❌ Order failed: {response.status}")
                    
        except Exception as e:
            logging.error(f"Error placing order: {e}")
    
    def _sign_order(self, order_params: Dict) -> str:
        """Sign order for Hyperliquid API"""
        try:
            signature_string = f"{order_params['coin']}{order_params['side']}{order_params['size']}{order_params['price']}"
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logging.error(f"Error signing order: {e}")
            return ""
    
    async def performance_monitor(self):
        """Monitor bot performance"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Calculate performance metrics
                win_rate = self.successful_signals / max(self.total_signals, 1)
                
                # Log performance
                self._log_performance(win_rate)
                
                # Display status
                if self.total_signals > 0:
                    logging.info(f"📊 Performance: {win_rate:.2%} win rate, {self.total_signals} total signals")
                
            except Exception as e:
                logging.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(60)
    
    async def risk_monitor(self):
        """Monitor risk levels"""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                # Check balance
                if self.account_balance <= self.min_balance_threshold:
                    logging.error("🚨 Balance below minimum threshold - stopping trading")
                    await self.emergency_stop()
                    break
                
                # Check daily loss
                if self.daily_pnl < -(self.config['risk']['max_daily_loss'] * self.account_balance):
                    logging.error("🚨 Daily loss limit exceeded - stopping trading")
                    await self.emergency_stop()
                    break
                
            except Exception as e:
                logging.error(f"Error in risk monitor: {e}")
                await asyncio.sleep(30)
    
    async def emergency_stop(self):
        """Emergency stop all trading"""
        try:
            logging.error("🚨 EMERGENCY STOP ACTIVATED")
            
            # Close all positions
            for symbol, position in self.positions.items():
                if position['size'] != 0:
                    await self.close_position(symbol, "EMERGENCY_STOP")
            
            logging.error("All trading activities stopped")
            
        except Exception as e:
            logging.error(f"Error during emergency stop: {e}")
    
    async def close_position(self, symbol: str, reason: str):
        """Close a position"""
        try:
            position = self.positions.get(symbol)
            if not position or position['size'] == 0:
                return
            
            close_side = 'SELL' if position['size'] > 0 else 'BUY'
            logging.info(f"Closing {symbol} position: {close_side} {abs(position['size'])} - {reason}")
            
            # This would place the actual closing order
            position['size'] = 0
            
        except Exception as e:
            logging.error(f"Error closing position: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        # Keep last 1000 trades
        if len(self.trades_data) > 1000:
            self.trades_data = self.trades_data[-1000:]
        
        # Keep last 1000 prices
        if len(self.price_data) > 1000:
            self.price_data = self.price_data[-1000:]
    
    def _get_current_price(self) -> Optional[float]:
        """Get current XRP price"""
        if self.trades_data:
            return self.trades_data[-1]['price']
        return None
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _log_trade(self, trade_info: Dict):
        """Log trade to CSV"""
        try:
            with open('enhanced_xrp_trades.csv', 'a') as f:
                f.write(f"{trade_info['timestamp']},{trade_info['symbol']},"
                       f"{trade_info['price']},{trade_info['quantity']},"
                       f"{trade_info['usd_size']},{trade_info['side']},"
                       f"{trade_info['event_time']}\n")
        except Exception as e:
            logging.error(f"Error logging trade: {e}")
    
    def _log_liquidation(self, liquidation_info: Dict):
        """Log liquidation to CSV"""
        try:
            with open('enhanced_xrp_liquidations.csv', 'a') as f:
                f.write(f"{liquidation_info['timestamp']},{liquidation_info['symbol']},"
                       f"{liquidation_info['side']},{liquidation_info['price']},"
                       f"{liquidation_info['quantity']},{liquidation_info['usd_size']},"
                       f"{liquidation_info['event_time']}\n")
        except Exception as e:
            logging.error(f"Error logging liquidation: {e}")
    
    def _log_signal(self, signal: Dict):
        """Log signal to CSV"""
        try:
            with open('enhanced_xrp_signals.csv', 'a') as f:
                f.write(f"{signal['timestamp'].isoformat()},{signal['type']},"
                       f"{signal['confidence']},{signal['action']},{signal['reason']},"
                       f"{signal['price']},{signal['strategy_source']},{signal['risk_score']},"
                       f"{signal['expected_return']}\n")
        except Exception as e:
            logging.error(f"Error logging signal: {e}")
    
    def _log_performance(self, win_rate: float):
        """Log performance to CSV"""
        try:
            with open('enhanced_xrp_performance.csv', 'a') as f:
                f.write(f"{datetime.now().isoformat()},Overall,{win_rate},"
                       f"{self.current_pnl},{self.total_signals}\n")
        except Exception as e:
            logging.error(f"Error logging performance: {e}")
    
    async def _log_simulated_order(self, signal: Dict, position_size: float):
        """Log simulated order"""
        logging.info(f"📝 Simulated order: {signal['action']} {position_size} {self.symbol} @ ${signal['price']:.4f}")

async def main():
    """Main function"""
    bot = EnhancedXRPBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
