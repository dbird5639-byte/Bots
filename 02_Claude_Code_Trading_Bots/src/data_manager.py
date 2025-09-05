"""
Data Manager Module

This module handles data collection, storage, and management
for market data and trading information.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import pandas as pd


class DataManager:
    """
    Manages market data collection, storage, and retrieval.
    """
    
    def __init__(self):
        """Initialize the data manager."""
        self.logger = logging.getLogger(__name__)
        self.market_data = {}
        self.data_sources = {}
        self.data_cache = {}
        self.last_update = {}
    
    async def fetch_market_data(self, 
                               symbol: str,
                               data_type: str = 'price',
                               timeframe: str = '1m',
                               limit: int = 1000) -> Dict[str, Any]:
        """
        Fetch market data for a specific symbol.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data (price, volume, orderbook, etc.)
            timeframe: Data timeframe
            limit: Number of data points to fetch
            
        Returns:
            Market data dictionary
        """
        try:
            cache_key = f"{symbol}_{data_type}_{timeframe}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Using cached data for {cache_key}")
                return self.data_cache[cache_key]
            
            # Fetch fresh data
            data = await self._fetch_from_source(symbol, data_type, timeframe, limit)
            
            # Cache the data
            self._cache_data(cache_key, data)
            
            # Update last update time
            self.last_update[cache_key] = datetime.now()
            
            self.logger.info(f"Fetched {len(data)} data points for {symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {e}")
            raise
    
    def store_market_data(self, 
                         symbol: str,
                         data: Dict[str, Any],
                         data_type: str = 'price') -> bool:
        """
        Store market data for a symbol.
        
        Args:
            symbol: Trading symbol
            data: Market data to store
            data_type: Type of data
            
        Returns:
            True if storage successful
        """
        try:
            if symbol not in self.market_data:
                self.market_data[symbol] = {}
            
            if data_type not in self.market_data[symbol]:
                self.market_data[symbol][data_type] = []
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            self.market_data[symbol][data_type].append(data)
            
            # Keep only recent data (last 1000 points)
            if len(self.market_data[symbol][data_type]) > 1000:
                self.market_data[symbol][data_type] = self.market_data[symbol][data_type][-1000:]
            
            self.logger.debug(f"Stored {data_type} data for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing market data for {symbol}: {e}")
            return False
    
    def get_market_data(self, 
                       symbol: str,
                       data_type: str = 'price',
                       start_time: datetime = None,
                       end_time: datetime = None) -> List[Dict[str, Any]]:
        """
        Retrieve stored market data for a symbol.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            List of market data points
        """
        try:
            if symbol not in self.market_data or data_type not in self.market_data[symbol]:
                return []
            
            data = self.market_data[symbol][data_type]
            
            # Apply time filters if specified
            if start_time or end_time:
                filtered_data = []
                for point in data:
                    point_time = datetime.fromisoformat(point['timestamp'])
                    
                    if start_time and point_time < start_time:
                        continue
                    if end_time and point_time > end_time:
                        continue
                    
                    filtered_data.append(point)
                
                return filtered_data
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error retrieving market data for {symbol}: {e}")
            return []
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest price or None
        """
        try:
            data = self.get_market_data(symbol, 'price', limit=1)
            if data:
                return float(data[-1].get('price', 0))
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
    
    def add_data_source(self, 
                       source_name: str,
                       source_config: Dict[str, Any]) -> bool:
        """
        Add a new data source.
        
        Args:
            source_name: Name of the data source
            source_config: Configuration for the data source
            
        Returns:
            True if addition successful
        """
        try:
            self.data_sources[source_name] = source_config
            self.logger.info(f"Added data source: {source_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding data source {source_name}: {e}")
            return False
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.last_update:
            return False
        
        # Cache expires after 1 minute
        cache_age = datetime.now() - self.last_update[cache_key]
        return cache_age < timedelta(minutes=1)
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache market data."""
        self.data_cache[cache_key] = data
        
        # Limit cache size
        if len(self.data_cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.data_cache.keys(), key=lambda k: self.last_update.get(k, datetime.min))
            del self.data_cache[oldest_key]
    
    async def _fetch_from_source(self, 
                                symbol: str,
                                data_type: str,
                                timeframe: str,
                                limit: int) -> Dict[str, Any]:
        """
        Fetch data from configured data sources.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data
            timeframe: Data timeframe
            limit: Number of data points
            
        Returns:
            Fetched data
        """
        # Simulate data fetching
        await asyncio.sleep(0.1)
        
        # Return mock data for demonstration
        mock_data = []
        base_time = datetime.now()
        
        for i in range(limit):
            timestamp = base_time - timedelta(minutes=i)
            mock_data.append({
                'timestamp': timestamp.isoformat(),
                'price': 100.0 + (i * 0.1),
                'volume': 1000 + (i * 10),
                'symbol': symbol
            })
        
        return mock_data
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of stored data."""
        summary = {
            'total_symbols': len(self.market_data),
            'total_data_points': sum(
                len(data_list) for symbol_data in self.market_data.values()
                for data_list in symbol_data.values()
            ),
            'data_sources': list(self.data_sources.keys()),
            'cache_size': len(self.data_cache),
            'last_updates': self.last_update
        }
        
        return summary
