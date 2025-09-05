"""
Market Analyzer Module

This module provides market analysis capabilities including
technical indicators, pattern recognition, and market sentiment analysis.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import math


class MarketAnalyzer:
    """
    Analyzes market data and provides trading insights.
    """
    
    def __init__(self):
        """Initialize the market analyzer."""
        self.logger = logging.getLogger(__name__)
        self.analysis_cache = {}
        self.technical_indicators = {}
    
    def analyze_market_conditions(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze overall market conditions.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Market analysis results
        """
        try:
            if not market_data:
                return {'error': 'No market data provided'}
            
            # Extract price data
            prices = [float(point.get('price', 0)) for point in market_data if point.get('price')]
            volumes = [float(point.get('volume', 0)) for point in market_data if point.get('volume')]
            
            if not prices:
                return {'error': 'No valid price data found'}
            
            # Calculate basic metrics
            analysis = {
                'current_price': prices[-1],
                'price_change': prices[-1] - prices[0],
                'price_change_percent': ((prices[-1] - prices[0]) / prices[0]) * 100,
                'volatility': self._calculate_volatility(prices),
                'trend': self._determine_trend(prices),
                'support_resistance': self._find_support_resistance(prices),
                'volume_analysis': self._analyze_volume(volumes),
                'technical_indicators': self._calculate_technical_indicators(prices),
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {e}")
            return {'error': str(e)}
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance) * 100  # Convert to percentage
    
    def _determine_trend(self, prices: List[float]) -> str:
        """Determine market trend."""
        if len(prices) < 20:
            return 'insufficient_data'
        
        # Simple moving average trend
        short_ma = sum(prices[-10:]) / 10
        long_ma = sum(prices[-20:]) / 20
        
        if short_ma > long_ma * 1.02:
            return 'uptrend'
        elif short_ma < long_ma * 0.98:
            return 'downtrend'
        else:
            return 'sideways'
    
    def _find_support_resistance(self, prices: List[float]) -> Dict[str, float]:
        """Find support and resistance levels."""
        if len(prices) < 20:
            return {'support': 0, 'resistance': 0}
        
        # Simple support/resistance using recent highs and lows
        recent_prices = prices[-20:]
        resistance = max(recent_prices)
        support = min(recent_prices)
        
        return {
            'support': support,
            'resistance': resistance,
            'range': resistance - support
        }
    
    def _analyze_volume(self, volumes: List[float]) -> Dict[str, Any]:
        """Analyze volume patterns."""
        if not volumes:
            return {'error': 'No volume data'}
        
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1] if volumes else 0
        
        return {
            'average_volume': avg_volume,
            'current_volume': current_volume,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0,
            'volume_trend': 'above_average' if current_volume > avg_volume else 'below_average'
        }
    
    def _calculate_technical_indicators(self, prices: List[float]) -> Dict[str, Any]:
        """Calculate technical indicators."""
        indicators = {}
        
        if len(prices) >= 14:
            indicators['rsi'] = self._calculate_rsi(prices)
        
        if len(prices) >= 20:
            indicators['sma_20'] = sum(prices[-20:]) / 20
            indicators['ema_20'] = self._calculate_ema(prices, 20)
        
        if len(prices) >= 50:
            indicators['sma_50'] = sum(prices[-50:]) / 50
        
        return indicators
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def get_market_sentiment(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze market sentiment.
        
        Args:
            market_data: Market data points
            
        Returns:
            Sentiment analysis results
        """
        try:
            analysis = self.analyze_market_conditions(market_data)
            
            if 'error' in analysis:
                return analysis
            
            # Determine sentiment based on analysis
            sentiment_score = 0
            
            # Trend contribution
            if analysis['trend'] == 'uptrend':
                sentiment_score += 30
            elif analysis['trend'] == 'downtrend':
                sentiment_score -= 30
            
            # Volatility contribution
            if analysis['volatility'] < 5:
                sentiment_score += 10  # Low volatility is generally positive
            elif analysis['volatility'] > 15:
                sentiment_score -= 10  # High volatility is generally negative
            
            # Volume contribution
            if analysis['volume_analysis'].get('volume_trend') == 'above_average':
                sentiment_score += 20
            else:
                sentiment_score -= 10
            
            # RSI contribution
            rsi = analysis['technical_indicators'].get('rsi', 50)
            if 30 <= rsi <= 70:
                sentiment_score += 10  # Neutral RSI
            elif rsi < 30:
                sentiment_score += 20  # Oversold (potential buy)
            elif rsi > 70:
                sentiment_score -= 20  # Overbought (potential sell)
            
            # Determine sentiment category
            if sentiment_score >= 50:
                sentiment = 'bullish'
            elif sentiment_score <= -50:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market sentiment: {e}")
            return {'error': str(e)}
    
    def get_trading_signals(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on market analysis.
        
        Args:
            market_data: Market data points
            
        Returns:
            List of trading signals
        """
        try:
            signals = []
            analysis = self.analyze_market_conditions(market_data)
            
            if 'error' in analysis:
                return signals
            
            current_price = analysis['current_price']
            rsi = analysis['technical_indicators'].get('rsi', 50)
            trend = analysis['trend']
            
            # RSI signals
            if rsi < 30:
                signals.append({
                    'type': 'buy',
                    'strength': 'strong',
                    'reason': f'RSI oversold ({rsi:.1f})',
                    'price': current_price,
                    'timestamp': datetime.now().isoformat()
                })
            elif rsi > 70:
                signals.append({
                    'type': 'sell',
                    'strength': 'strong',
                    'reason': f'RSI overbought ({rsi:.1f})',
                    'price': current_price,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Trend signals
            if trend == 'uptrend' and rsi < 40:
                signals.append({
                    'type': 'buy',
                    'strength': 'medium',
                    'reason': f'Uptrend with RSI pullback ({rsi:.1f})',
                    'price': current_price,
                    'timestamp': datetime.now().isoformat()
                })
            elif trend == 'downtrend' and rsi > 60:
                signals.append({
                    'type': 'sell',
                    'strength': 'medium',
                    'reason': f'Downtrend with RSI bounce ({rsi:.1f})',
                    'price': current_price,
                    'timestamp': datetime.now().isoformat()
                })
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating trading signals: {e}")
            return []
