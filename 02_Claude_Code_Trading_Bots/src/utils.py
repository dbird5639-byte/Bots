"""
Trading Utilities Module

This module provides utility functions and helper classes
for the trading bot system.
"""

import hashlib
import secrets
import time
import json
import math
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import asyncio


class TradingUtils:
    """
    Utility functions for trading operations.
    """
    
    @staticmethod
    def generate_trade_id() -> str:
        """Generate a unique trade ID."""
        timestamp = int(time.time() * 1000)
        random_part = secrets.token_hex(4)
        return f"trade_{timestamp}_{random_part}"
    
    @staticmethod
    def generate_strategy_id() -> str:
        """Generate a unique strategy ID."""
        timestamp = int(time.time() * 1000)
        random_part = secrets.token_hex(4)
        return f"strategy_{timestamp}_{random_part}"
    
    @staticmethod
    def calculate_position_size(capital: float, risk_per_trade: float, 
                              entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            capital: Available capital
            risk_per_trade: Risk per trade as percentage
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Position size in units
        """
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0
        
        risk_amount = capital * risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0.0
        
        position_size = risk_amount / risk_per_unit
        return position_size
    
    @staticmethod
    def calculate_risk_reward_ratio(entry_price: float, stop_loss: float, 
                                   take_profit: float) -> float:
        """
        Calculate risk-reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Risk-reward ratio
        """
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return 0.0
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0.0
        
        return reward / risk
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """
        Calculate percentage change between two values.
        
        Args:
            old_value: Old value
            new_value: New value
            
        Returns:
            Percentage change
        """
        if old_value == 0:
            return 0.0
        
        return ((new_value - old_value) / old_value) * 100
    
    @staticmethod
    def calculate_compound_return(initial_capital: float, final_capital: float, 
                                 periods: int) -> float:
        """
        Calculate compound annual return.
        
        Args:
            initial_capital: Initial capital
            final_capital: Final capital
            periods: Number of periods
            
        Returns:
            Compound annual return as percentage
        """
        if initial_capital <= 0 or periods <= 0:
            return 0.0
        
        if final_capital <= 0:
            return -100.0
        
        ratio = final_capital / initial_capital
        compound_return = (ratio ** (1 / periods) - 1) * 100
        
        return compound_return
    
    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """
        Calculate price volatility.
        
        Args:
            prices: List of prices
            
        Returns:
            Volatility as percentage
        """
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
        volatility = math.sqrt(variance) * 100
        
        return volatility
    
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> List[float]:
        """
        Calculate simple moving average.
        
        Args:
            prices: List of prices
            period: Moving average period
            
        Returns:
            List of moving average values
        """
        if len(prices) < period:
            return []
        
        moving_averages = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i-period+1:i+1]) / period
            moving_averages.append(avg)
        
        return moving_averages
    
    @staticmethod
    def calculate_exponential_moving_average(prices: List[float], period: int) -> List[float]:
        """
        Calculate exponential moving average.
        
        Args:
            prices: List of prices
            period: EMA period
            
        Returns:
            List of EMA values
        """
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # First EMA is simple average
        first_ema = sum(prices[:period]) / period
        ema_values.append(first_ema)
        
        # Calculate subsequent EMAs
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                 std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of prices
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = TradingUtils.calculate_moving_average(prices, period)
        
        if not sma:
            return {'upper': [], 'middle': [], 'lower': []}
        
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            # Calculate standard deviation for this period
            period_prices = prices[i-period+1:i+1]
            period_mean = sma[i-period+1] if i-period+1 < len(sma) else sma[-1]
            
            variance = sum((p - period_mean) ** 2 for p in period_prices) / period
            std = math.sqrt(variance)
            
            upper = period_mean + (std_dev * std)
            lower = period_mean - (std_dev * std)
            
            upper_band.append(upper)
            lower_band.append(lower)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: List of prices
            period: RSI period
            
        Returns:
            List of RSI values
        """
        if len(prices) < period + 1:
            return []
        
        rsi_values = []
        gains = []
        losses = []
        
        # Calculate gains and losses
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate initial averages
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate first RSI
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
        
        # Calculate subsequent RSIs
        for i in range(period, len(prices)):
            gain = gains[i-1]
            loss = losses[i-1]
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    @staticmethod
    def format_number(number: float, decimal_places: int = 4) -> str:
        """
        Format number with specified decimal places.
        
        Args:
            number: Number to format
            decimal_places: Number of decimal places
            
        Returns:
            Formatted number string
        """
        return f"{number:.{decimal_places}f}"
    
    @staticmethod
    def format_currency(amount: float, currency: str = "USD") -> str:
        """
        Format amount as currency.
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """
        Format value as percentage.
        
        Args:
            value: Value to format
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers, returning default if denominator is zero.
        
        Args:
            numerator: Numerator
            denominator: Denominator
            default: Default value if division by zero
            
        Returns:
            Division result or default value
        """
        if denominator == 0:
            return default
        return numerator / denominator
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp value between minimum and maximum.
        
        Args:
            value: Value to clamp
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Clamped value
        """
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def is_business_day(date: datetime) -> bool:
        """
        Check if date is a business day (Monday-Friday).
        
        Args:
            date: Date to check
            
        Returns:
            True if business day
        """
        return date.weekday() < 5  # Monday = 0, Friday = 4
    
    @staticmethod
    def get_next_business_day(date: datetime) -> datetime:
        """
        Get next business day.
        
        Args:
            date: Starting date
            
        Returns:
            Next business day
        """
        next_day = date + timedelta(days=1)
        while not TradingUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    @staticmethod
    def hash_string(text: str) -> str:
        """
        Create SHA-256 hash of string.
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def generate_random_string(length: int = 16) -> str:
        """
        Generate random string.
        
        Args:
            length: String length
            
        Returns:
            Random string
        """
        return secrets.token_hex(length // 2)
    
    @staticmethod
    async def delay(seconds: float):
        """
        Asynchronous delay.
        
        Args:
            seconds: Delay duration in seconds
        """
        await asyncio.sleep(seconds)
    
    @staticmethod
    def retry_on_exception(func, max_retries: int = 3, delay_seconds: float = 1.0):
        """
        Retry function on exception.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            delay_seconds: Delay between retries
            
        Returns:
            Function result
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay_seconds)
    
    @staticmethod
    def validate_json(data: str) -> bool:
        """
        Validate JSON string.
        
        Args:
            data: JSON string to validate
            
        Returns:
            True if valid JSON
        """
        try:
            json.loads(data)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = TradingUtils.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
