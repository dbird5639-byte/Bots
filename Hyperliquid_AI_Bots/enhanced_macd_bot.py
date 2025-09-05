"""
Enhanced AI-Powered MACD Trading Bot for Hyperliquid

This bot uses advanced MACD analysis with AI-powered signal filtering,
multi-timeframe analysis, and dynamic risk management.
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
        logging.FileHandler('enhanced_macd_bot.log'),
        logging.StreamHandler()
    ]
)

class EnhancedMACDBot:
    """
    Enhanced AI-Powered MACD Trading Bot
    
    Features:
    - Multi-timeframe MACD analysis
    - AI-powered signal filtering
    - Dynamic risk management
    - Volume confirmation
    - Trend strength analysis
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
        
        # MACD settings
        self.macd_fast = self.config['macd']['fast_period']
        self.macd_slow = self.config['macd']['slow_period']
        self.macd_signal = self.config['macd']['signal_period']
        self.macd_threshold = self.config['macd']['threshold']
        
        # Multi-timeframe settings
        self.timeframes = self.config['timeframes']
        self.timeframe_data = {}
        
        # Data storage
        self.trades_data = []
        self.price_data = []
        self.macd_signals = []
        self.positions = {}
        
        # Performance tracking
        self.total_signals = 0
        self.successful_signals = 0
        self.current_pnl = 0.0
        self.daily_pnl = 0.0
        
        # API credentials
        self.api_key = os.getenv('HYPERLIQUID_API_KEY')
        self.api_secret = os.getenv('HYPERLIQUID_API_SECRET')
        
        # Session
        self.session = None
        
        # Initialize files
        self._initialize_files()
        
        logging.info("Enhanced MACD Bot initialized")
    
    def _load_config(self) -> Dict:
        """Load bot configuration"""
        return {
            'account': {
                'balance': 60,
                'min_balance': 10,
                'leverage': 1,
                'max_leverage': 1
            },
            'macd': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9,
                'threshold': 0.0001,
                'confirmation_periods': 3
            },
            'timeframes': ['1m', '5m', '15m', '1h', '4h'],
            'risk': {
                'max_position_size': 0.05,
                'max_total_exposure': 0.15,
                'default_stop_loss': 0.03,
                'default_take_profit': 0.10,
                'max_daily_loss': 0.03
            },
            'ai': {
                'confidence_threshold': 0.7,
                'volume_confirmation': True,
                'trend_strength_filter': True,
                'signal_validation': True
            }
        }
    
    def _initialize_files(self):
        """Initialize data files"""
        files = [
            'enhanced_macd_trades.csv',
            'enhanced_macd_signals.csv',
            'enhanced_macd_performance.csv',
            'enhanced_macd_macd_data.csv'
        ]
        
        for filename in files:
            if not os.path.isfile(filename):
                with open(filename, 'w') as f:
                    if 'trades' in filename:
                        f.write('timestamp,symbol,price,quantity,usd_size,side,event_time\n')
                    elif 'signals' in filename:
                        f.write('timestamp,signal_type,confidence,action,reason,price,macd_value,signal_strength\n')
                    elif 'performance' in filename:
                        f.write('timestamp,strategy,win_rate,profit_factor,sharpe_ratio,total_pnl\n')
                    elif 'macd_data' in filename:
                        f.write('timestamp,timeframe,macd_line,signal_line,histogram,price\n')
    
    async def start_bot(self):
        """Start the enhanced MACD bot"""
        logging.info("🚀 Starting Enhanced MACD Bot...")
        
        # Initialize session
        self.session = aiohttp.ClientSession()
        
        try:
            # Verify settings
            await self.verify_settings()
            
            # Create tasks
            tasks = [
                self.data_stream_manager(),
                self.macd_analyzer(),
                self.signal_generator(),
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
        """Manage data streams"""
        try:
            # Start data streams
            streams = [
                self.hyperliquid_trade_stream(),
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
            
            # Store trade data
            self.trades_data.append(trade_info)
            self.price_data.append(trade_info['price'])
            
            # Keep recent data
            self._cleanup_old_data()
            
            # Log trade
            self._log_trade(trade_info)
            
        except Exception as e:
            logging.error(f"Error processing trade: {e}")
    
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
                    # Update spread information
                    spread = best_ask - best_bid
                    spread_pct = (spread / best_bid) * 100
                    
                    # Log spread for analysis
                    if spread_pct < 0.1:  # Very tight spread
                        logging.info(f"Tight spread detected: {spread_pct:.3f}%")
                        
        except Exception as e:
            logging.error(f"Error processing order book: {e}")
    
    async def macd_analyzer(self):
        """Analyze MACD indicators for all timeframes"""
        while True:
            try:
                await asyncio.sleep(10)  # Analyze every 10 seconds
                
                if len(self.price_data) < self.macd_slow:
                    continue
                
                # Calculate MACD for different timeframes
                for timeframe in self.timeframes:
                    await self.calculate_macd_timeframe(timeframe)
                
                # Generate MACD signals
                await self.generate_macd_signals()
                
            except Exception as e:
                logging.error(f"Error in MACD analyzer: {e}")
                await asyncio.sleep(5)
    
    async def calculate_macd_timeframe(self, timeframe: str):
        """Calculate MACD for a specific timeframe"""
        try:
            # Get price data for timeframe
            if timeframe == '1m':
                prices = self.price_data[-100:]  # Last 100 prices
            elif timeframe == '5m':
                prices = self.price_data[-300:]  # Last 300 prices
            elif timeframe == '15m':
                prices = self.price_data[-900:]  # Last 900 prices
            elif timeframe == '1h':
                prices = self.price_data[-3600:]  # Last 3600 prices
            elif timeframe == '4h':
                prices = self.price_data[-14400:]  # Last 14400 prices
            else:
                prices = self.price_data[-100:]
            
            if len(prices) < self.macd_slow:
                return
            
            # Calculate MACD
            macd_line, signal_line, histogram = self._calculate_macd(prices)
            
            # Store MACD data
            if timeframe not in self.timeframe_data:
                self.timeframe_data[timeframe] = []
            
            macd_data = {
                'timestamp': datetime.now(),
                'timeframe': timeframe,
                'macd_line': macd_line,
                'signal_line': signal_line,
                'histogram': histogram,
                'price': prices[-1] if prices else 0
            }
            
            self.timeframe_data[timeframe].append(macd_data)
            
            # Keep only recent data
            if len(self.timeframe_data[timeframe]) > 100:
                self.timeframe_data[timeframe] = self.timeframe_data[timeframe][-100:]
            
            # Log MACD data
            self._log_macd_data(macd_data)
            
        except Exception as e:
            logging.error(f"Error calculating MACD for {timeframe}: {e}")
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD indicator"""
        try:
            if len(prices) < self.macd_slow:
                return 0.0, 0.0, 0.0
            
            # Calculate EMAs
            ema_fast = self._calculate_ema(prices, self.macd_fast)
            ema_slow = self._calculate_ema(prices, self.macd_slow)
            
            # MACD line
            macd_line = ema_fast - ema_slow
            
            # Signal line (EMA of MACD line)
            if len(self.timeframe_data.get('1m', [])) > self.macd_signal:
                macd_values = [d['macd_line'] for d in self.timeframe_data['1m'][-self.macd_signal:]]
                signal_line = np.mean(macd_values)
            else:
                signal_line = macd_line
            
            # Histogram
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            logging.error(f"Error calculating MACD: {e}")
            return 0.0, 0.0, 0.0
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0
            
            # Simple EMA calculation
            alpha = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = alpha * price + (1 - alpha) * ema
            
            return ema
            
        except Exception as e:
            logging.error(f"Error calculating EMA: {e}")
            return prices[-1] if prices else 0
    
    async def generate_macd_signals(self):
        """Generate MACD-based trading signals"""
        try:
            # Check for MACD crossovers
            for timeframe in self.timeframes:
                if timeframe not in self.timeframe_data or len(self.timeframe_data[timeframe]) < 2:
                    continue
                
                current_data = self.timeframe_data[timeframe][-1]
                previous_data = self.timeframe_data[timeframe][-2]
                
                # Check for MACD crossover
                if (previous_data['macd_line'] < previous_data['signal_line'] and 
                    current_data['macd_line'] > current_data['signal_line']):
                    # Bullish crossover
                    await self.generate_bullish_signal(timeframe, current_data)
                    
                elif (previous_data['macd_line'] > previous_data['signal_line'] and 
                      current_data['macd_line'] < current_data['signal_line']):
                    # Bearish crossover
                    await self.generate_bearish_signal(timeframe, current_data)
                
                # Check for histogram divergence
                await self.check_histogram_divergence(timeframe, current_data)
                
        except Exception as e:
            logging.error(f"Error generating MACD signals: {e}")
    
    async def generate_bullish_signal(self, timeframe: str, macd_data: Dict):
        """Generate bullish MACD signal"""
        try:
            # Calculate signal strength
            signal_strength = abs(macd_data['histogram']) / self.macd_threshold
            
            # Check volume confirmation
            volume_confirmed = await self.check_volume_confirmation('BUY')
            
            # Check trend strength
            trend_confirmed = await self.check_trend_strength('UP')
            
            # Calculate confidence
            confidence = min(0.8, 0.5 + (signal_strength * 0.3))
            if volume_confirmed:
                confidence += 0.1
            if trend_confirmed:
                confidence += 0.1
            
            if confidence >= self.config['ai']['confidence_threshold']:
                signal = {
                    'type': 'MACD_BULLISH',
                    'confidence': confidence,
                    'action': 'BUY',
                    'reason': f"MACD bullish crossover on {timeframe} timeframe",
                    'price': macd_data['price'],
                    'macd_value': macd_data['macd_line'],
                    'signal_strength': signal_strength,
                    'timestamp': datetime.now(),
                    'timeframe': timeframe
                }
                
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating bullish signal: {e}")
    
    async def generate_bearish_signal(self, timeframe: str, macd_data: Dict):
        """Generate bearish MACD signal"""
        try:
            # Calculate signal strength
            signal_strength = abs(macd_data['histogram']) / self.macd_threshold
            
            # Check volume confirmation
            volume_confirmed = await self.check_volume_confirmation('SELL')
            
            # Check trend strength
            trend_confirmed = await self.check_trend_strength('DOWN')
            
            # Calculate confidence
            confidence = min(0.8, 0.5 + (signal_strength * 0.3))
            if volume_confirmed:
                confidence += 0.1
            if trend_confirmed:
                confidence += 0.1
            
            if confidence >= self.config['ai']['confidence_threshold']:
                signal = {
                    'type': 'MACD_BEARISH',
                    'confidence': confidence,
                    'action': 'SELL',
                    'reason': f"MACD bearish crossover on {timeframe} timeframe",
                    'price': macd_data['price'],
                    'macd_value': macd_data['macd_line'],
                    'signal_strength': signal_strength,
                    'timestamp': datetime.now(),
                    'timeframe': timeframe
                }
                
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating bearish signal: {e}")
    
    async def check_histogram_divergence(self, timeframe: str, macd_data: Dict):
        """Check for histogram divergence patterns"""
        try:
            if len(self.timeframe_data[timeframe]) < 10:
                return
            
            # Get recent histogram data
            recent_histograms = [d['histogram'] for d in self.timeframe_data[timeframe][-10:]]
            recent_prices = [d['price'] for d in self.timeframe_data[timeframe][-10:]]
            
            # Check for bullish divergence (price lower, histogram higher)
            if (recent_prices[-1] < recent_prices[0] and 
                recent_histograms[-1] > recent_histograms[0]):
                
                signal = {
                    'type': 'MACD_BULLISH_DIVERGENCE',
                    'confidence': 0.75,
                    'action': 'BUY',
                    'reason': f"Bullish divergence on {timeframe} timeframe",
                    'price': macd_data['price'],
                    'macd_value': macd_data['macd_line'],
                    'signal_strength': 1.0,
                    'timestamp': datetime.now(),
                    'timeframe': timeframe
                }
                
                await self.execute_signal(signal)
            
            # Check for bearish divergence (price higher, histogram lower)
            elif (recent_prices[-1] > recent_prices[0] and 
                  recent_histograms[-1] < recent_histograms[0]):
                
                signal = {
                    'type': 'MACD_BEARISH_DIVERGENCE',
                    'confidence': 0.75,
                    'action': 'SELL',
                    'reason': f"Bearish divergence on {timeframe} timeframe",
                    'price': macd_data['price'],
                    'macd_value': macd_data['macd_line'],
                    'signal_strength': 1.0,
                    'timestamp': datetime.now(),
                    'timeframe': timeframe
                }
                
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error checking histogram divergence: {e}")
    
    async def check_volume_confirmation(self, action: str) -> bool:
        """Check if volume confirms the signal"""
        try:
            if not self.config['ai']['volume_confirmation']:
                return True
            
            if len(self.trades_data) < 20:
                return False
            
            # Get recent volume data
            recent_volumes = [t['usd_size'] for t in self.trades_data[-20:]]
            avg_volume = np.mean(recent_volumes)
            current_volume = sum([t['usd_size'] for t in self.trades_data[-5:]])
            
            # Volume should be above average for confirmation
            return current_volume > avg_volume * 1.2
            
        except Exception as e:
            logging.error(f"Error checking volume confirmation: {e}")
            return False
    
    async def check_trend_strength(self, direction: str) -> bool:
        """Check trend strength"""
        try:
            if not self.config['ai']['trend_strength_filter']:
                return True
            
            if len(self.price_data) < 20:
                return False
            
            # Calculate trend strength
            recent_prices = self.price_data[-20:]
            if direction == 'UP':
                up_moves = sum(1 for i in range(1, len(recent_prices)) 
                             if recent_prices[i] > recent_prices[i-1])
                trend_strength = up_moves / (len(recent_prices) - 1)
            else:  # DOWN
                down_moves = sum(1 for i in range(1, len(recent_prices)) 
                               if recent_prices[i] < recent_prices[i-1])
                trend_strength = down_moves / (len(recent_prices) - 1)
            
            # Trend should be strong (60%+ moves in the direction)
            return trend_strength >= 0.6
            
        except Exception as e:
            logging.error(f"Error checking trend strength: {e}")
            return False
    
    async def signal_generator(self):
        """Generate additional trading signals"""
        while True:
            try:
                await asyncio.sleep(60)  # Generate signals every minute
                
                # Generate trend following signals
                await self.generate_trend_signals()
                
                # Generate momentum signals
                await self.generate_momentum_signals()
                
            except Exception as e:
                logging.error(f"Error in signal generator: {e}")
                await asyncio.sleep(5)
    
    async def generate_trend_signals(self):
        """Generate trend following signals"""
        try:
            if len(self.price_data) < 50:
                return
            
            # Calculate trend
            recent_prices = self.price_data[-50:]
            trend_slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            
            # Generate trend signals
            if trend_slope > 0.001:  # Strong uptrend
                signal = {
                    'type': 'TREND_UP',
                    'confidence': 0.6,
                    'action': 'BUY',
                    'reason': f"Strong uptrend detected (slope: {trend_slope:.6f})",
                    'price': self.price_data[-1],
                    'macd_value': 0,
                    'signal_strength': 0.8,
                    'timestamp': datetime.now(),
                    'timeframe': 'TREND'
                }
                await self.execute_signal(signal)
                
            elif trend_slope < -0.001:  # Strong downtrend
                signal = {
                    'type': 'TREND_DOWN',
                    'confidence': 0.6,
                    'action': 'SELL',
                    'reason': f"Strong downtrend detected (slope: {trend_slope:.6f})",
                    'price': self.price_data[-1],
                    'macd_value': 0,
                    'signal_strength': 0.8,
                    'timestamp': datetime.now(),
                    'timeframe': 'TREND'
                }
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating trend signals: {e}")
    
    async def generate_momentum_signals(self):
        """Generate momentum-based signals"""
        try:
            if len(self.price_data) < 20:
                return
            
            # Calculate momentum
            recent_prices = self.price_data[-20:]
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # Generate momentum signals
            if momentum > 0.05:  # Strong positive momentum
                signal = {
                    'type': 'MOMENTUM_UP',
                    'confidence': 0.55,
                    'action': 'BUY',
                    'reason': f"Strong positive momentum: {momentum:.2%}",
                    'price': self.price_data[-1],
                    'macd_value': 0,
                    'signal_strength': 0.7,
                    'timestamp': datetime.now(),
                    'timeframe': 'MOMENTUM'
                }
                await self.execute_signal(signal)
                
            elif momentum < -0.05:  # Strong negative momentum
                signal = {
                    'type': 'MOMENTUM_DOWN',
                    'confidence': 0.55,
                    'action': 'SELL',
                    'reason': f"Strong negative momentum: {momentum:.2%}",
                    'price': self.price_data[-1],
                    'macd_value': 0,
                    'signal_strength': 0.7,
                    'timestamp': datetime.now(),
                    'timeframe': 'MOMENTUM'
                }
                await self.execute_signal(signal)
                
        except Exception as e:
            logging.error(f"Error generating momentum signals: {e}")
    
    async def execute_signal(self, signal: Dict):
        """Execute a trading signal"""
        try:
            logging.info(f"🎯 Executing signal: {signal['type']} - {signal['action']}")
            logging.info(f"Confidence: {signal['confidence']:.2%}, Strength: {signal['signal_strength']:.2f}")
            
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
            
            # Check balance
            if self.account_balance <= self.min_balance_threshold:
                return False
            
            # Check for recent similar signals
            if await self.check_signal_frequency(signal):
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating signal: {e}")
            return False
    
    async def check_signal_frequency(self, signal: Dict) -> bool:
        """Check if too many similar signals recently"""
        try:
            # Check last 10 minutes for similar signals
            recent_signals = [
                s for s in self.macd_signals 
                if (datetime.now() - s['timestamp']).total_seconds() < 600
                and s['type'] == signal['type']
            ]
            
            # Allow max 2 similar signals per 10 minutes
            return len(recent_signals) >= 2
            
        except Exception as e:
            logging.error(f"Error checking signal frequency: {e}")
            return False
    
    async def calculate_position_size(self, signal: Dict) -> float:
        """Calculate optimal position size"""
        try:
            # Base position size (0.5% of balance for 1x leverage)
            base_size = self.account_balance * 0.005
            
            # Adjust based on confidence and signal strength
            confidence_multiplier = signal['confidence']
            strength_multiplier = min(signal['signal_strength'], 1.0)
            
            position_size = base_size * confidence_multiplier * strength_multiplier
            
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
    
    def _log_trade(self, trade_info: Dict):
        """Log trade to CSV"""
        try:
            with open('enhanced_macd_trades.csv', 'a') as f:
                f.write(f"{trade_info['timestamp']},{trade_info['symbol']},"
                       f"{trade_info['price']},{trade_info['quantity']},"
                       f"{trade_info['usd_size']},{trade_info['side']},"
                       f"{trade_info['event_time']}\n")
        except Exception as e:
            logging.error(f"Error logging trade: {e}")
    
    def _log_signal(self, signal: Dict):
        """Log signal to CSV"""
        try:
            with open('enhanced_macd_signals.csv', 'a') as f:
                f.write(f"{signal['timestamp'].isoformat()},{signal['type']},"
                       f"{signal['confidence']},{signal['action']},{signal['reason']},"
                       f"{signal['price']},{signal['macd_value']},{signal['signal_strength']}\n")
        except Exception as e:
            logging.error(f"Error logging signal: {e}")
    
    def _log_macd_data(self, macd_data: Dict):
        """Log MACD data to CSV"""
        try:
            with open('enhanced_macd_macd_data.csv', 'a') as f:
                f.write(f"{macd_data['timestamp'].isoformat()},{macd_data['timeframe']},"
                       f"{macd_data['macd_line']},{macd_data['signal_line']},"
                       f"{macd_data['histogram']},{macd_data['price']}\n")
        except Exception as e:
            logging.error(f"Error logging MACD data: {e}")
    
    def _log_performance(self, win_rate: float):
        """Log performance to CSV"""
        try:
            with open('enhanced_macd_performance.csv', 'a') as f:
                f.write(f"{datetime.now().isoformat()},MACD,{win_rate},"
                       f"{self.current_pnl},{self.total_signals}\n")
        except Exception as e:
            logging.error(f"Error logging performance: {e}")
    
    async def _log_simulated_order(self, signal: Dict, position_size: float):
        """Log simulated order"""
        logging.info(f"📝 Simulated order: {signal['action']} {position_size} {self.symbol} @ ${signal['price']:.4f}")

async def main():
    """Main function"""
    bot = EnhancedMACDBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
