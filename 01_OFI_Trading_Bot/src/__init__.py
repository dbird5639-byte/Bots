"""
OFI Trading Bot - Source Package

This package contains the core components of the Order Flow Imbalance trading bot.
"""

__version__ = "1.0.0"
__author__ = "Trading Bot Community"
__description__ = "Advanced order flow imbalance trading bot"

from .main import TradingBot
from .ofi_analyzer import OFIAnalyzer
from .signal_generator import SignalGenerator
from .risk_manager import RiskManager
from .exchange_connector import ExchangeConnector

__all__ = [
    "TradingBot",
    "OFIAnalyzer", 
    "SignalGenerator",
    "RiskManager",
    "ExchangeConnector"
]
