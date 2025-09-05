"""
Claude Code Trading Bots - Source Package

This package contains the core components of the AI-powered trading bot system
that leverages Claude Code for strategy generation, optimization, and execution.
"""

__version__ = "2.0.0"
__author__ = "Claude Code Trading Community"
__description__ = "AI-powered trading bot framework using Claude Code"

# Core AI components
from .ai_manager import AIManager
from .claude_integration import ClaudeIntegration
from .strategy_generator import StrategyGenerator
from .code_optimizer import CodeOptimizer

# Trading components
from .trading_bot import ClaudeTradingBot
from .strategy_executor import StrategyExecutor
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager

# Data and analysis
from .data_manager import DataManager
from .market_analyzer import MarketAnalyzer
from .performance_tracker import PerformanceTracker

# Utilities
from .config_manager import ConfigManager
from .logger import Logger
from .utils import TradingUtils

__all__ = [
    # AI Components
    "AIManager",
    "ClaudeIntegration", 
    "StrategyGenerator",
    "CodeOptimizer",
    
    # Trading Components
    "ClaudeTradingBot",
    "StrategyExecutor",
    "RiskManager",
    "PortfolioManager",
    
    # Data and Analysis
    "DataManager",
    "MarketAnalyzer",
    "PerformanceTracker",
    
    # Utilities
    "ConfigManager",
    "Logger",
    "TradingUtils"
]
