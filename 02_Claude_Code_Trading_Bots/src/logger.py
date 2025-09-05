"""
Logger Module

This module provides centralized logging functionality
for the trading bot system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class Logger:
    """
    Centralized logging system for the trading bot.
    """
    
    def __init__(self, 
                 name: str = "TradingBot",
                 log_level: str = "INFO",
                 log_file: str = None,
                 max_file_size: int = 10485760,  # 10MB
                 backup_count: int = 5):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            log_level: Logging level
            log_file: Path to log file
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Initialize logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger with handlers and formatters."""
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if log_file specified)
        if self.log_file:
            file_handler = self._create_file_handler(formatter)
            if file_handler:
                logger.addHandler(file_handler)
        
        return logger
    
    def _create_file_handler(self, formatter: logging.Formatter) -> Optional[logging.handlers.RotatingFileHandler]:
        """Create rotating file handler for logging."""
        try:
            log_path = Path(self.log_file)
            log_dir = log_path.parent
            
            # Create log directory if it doesn't exist
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            
            return file_handler
            
        except Exception as e:
            print(f"Error creating file handler: {e}")
            return None
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception message with traceback."""
        self.logger.exception(message, *args, **kwargs)
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """
        Log trade information.
        
        Args:
            trade_data: Trade data dictionary
        """
        try:
            trade_info = f"TRADE: {trade_data.get('symbol', 'Unknown')} - "
            trade_info += f"{trade_data.get('action', 'Unknown')} - "
            trade_info += f"Price: {trade_data.get('price', 0):.4f} - "
            trade_info += f"Quantity: {trade_data.get('quantity', 0):.4f}"
            
            if 'pnl' in trade_data:
                trade_info += f" - PnL: {trade_data['pnl']:.2f}"
            
            self.info(trade_info)
            
        except Exception as e:
            self.error(f"Error logging trade: {e}")
    
    def log_strategy(self, strategy_data: Dict[str, Any]):
        """
        Log strategy information.
        
        Args:
            strategy_data: Strategy data dictionary
        """
        try:
            strategy_info = f"STRATEGY: {strategy_data.get('name', 'Unknown')} - "
            strategy_info += f"Status: {strategy_data.get('status', 'Unknown')} - "
            strategy_info += f"Type: {strategy_data.get('type', 'Unknown')}"
            
            if 'performance' in strategy_data:
                perf = strategy_data['performance']
                strategy_info += f" - Return: {perf.get('return', 0):.2f}%"
                strategy_info += f" - Drawdown: {perf.get('drawdown', 0):.2f}%"
            
            self.info(strategy_info)
            
        except Exception as e:
            self.error(f"Error logging strategy: {e}")
    
    def log_performance(self, performance_data: Dict[str, Any]):
        """
        Log performance metrics.
        
        Args:
            performance_data: Performance data dictionary
        """
        try:
            perf_info = f"PERFORMANCE: Total Return: {performance_data.get('total_return', 0):.2f}% - "
            perf_info += f"Win Rate: {performance_data.get('win_rate', 0):.1f}% - "
            perf_info += f"Sharpe: {performance_data.get('sharpe_ratio', 0):.2f} - "
            perf_info += f"Max DD: {performance_data.get('max_drawdown', 0):.2f}%"
            
            self.info(perf_info)
            
        except Exception as e:
            self.error(f"Error logging performance: {e}")
    
    def log_error(self, error: Exception, context: str = ""):
        """
        Log error with context.
        
        Args:
            error: Exception object
            context: Additional context information
        """
        try:
            error_msg = f"ERROR in {context}: {type(error).__name__}: {str(error)}"
            self.error(error_msg)
            
            # Log full traceback for debugging
            self.exception(f"Full traceback for error in {context}")
            
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def log_system_status(self, status_data: Dict[str, Any]):
        """
        Log system status information.
        
        Args:
            status_data: System status data
        """
        try:
            status_info = f"SYSTEM STATUS: Bot: {status_data.get('bot_status', 'Unknown')} - "
            status_info += f"AI: {status_data.get('ai_status', 'Unknown')} - "
            status_info += f"Trading: {status_data.get('trading_status', 'Unknown')} - "
            status_info += f"Data: {status_data.get('data_status', 'Unknown')}"
            
            self.info(status_info)
            
        except Exception as e:
            self.error(f"Error logging system status: {e}")
    
    def set_level(self, level: str):
        """
        Set logging level.
        
        Args:
            level: Logging level string
        """
        try:
            new_level = getattr(logging, level.upper(), logging.INFO)
            self.log_level = new_level
            self.logger.setLevel(new_level)
            
            # Update all handlers
            for handler in self.logger.handlers:
                handler.setLevel(new_level)
            
            self.info(f"Log level changed to {level.upper()}")
            
        except Exception as e:
            self.error(f"Error setting log level: {e}")
    
    def add_file_handler(self, log_file: str):
        """
        Add a new file handler.
        
        Args:
            log_file: Path to log file
        """
        try:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler = self._create_file_handler(formatter)
            if file_handler:
                self.logger.addHandler(file_handler)
                self.info(f"Added file handler: {log_file}")
            
        except Exception as e:
            self.error(f"Error adding file handler: {e}")
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logging.Logger instance."""
        return self.logger
    
    def close(self):
        """Close all handlers and cleanup."""
        try:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
            
            self.info("Logger closed successfully")
            
        except Exception as e:
            print(f"Error closing logger: {e}")
