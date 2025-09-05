"""
Enhanced AI Bot Configuration

This file contains all configurable parameters for the enhanced AI trading bots.
Modify these values to adjust bot behavior without changing the main code.
"""

# =============================================================================
# ACCOUNT & LEVERAGE SETTINGS
# =============================================================================
ACCOUNT_CONFIG = {
    'balance': 60,  # Your account balance in USD
    'min_balance': 10,  # Minimum balance to maintain (stop trading if below)
    'leverage': 1,  # 1x leverage (no leverage)
    'max_leverage': 1,  # Maximum leverage allowed (set to 1 for no leverage)
    'enable_leverage_warnings': True,  # Warn if leverage exceeds 1x
}

# =============================================================================
# HYPERLIQUID EXCHANGE CONFIGURATION
# =============================================================================
HYPERLIQUID_CONFIG = {
    'name': 'Hyperliquid',
    'base_url': 'https://api.hyperliquid.xyz',
    'ws_url': 'wss://api.hyperliquid.xyz/ws',
    'symbol': 'XRP',  # Hyperliquid uses 'XRP' not 'XRPUSDT'
    'testnet': False,  # Set to True for testing
}

# =============================================================================
# API CREDENTIALS
# =============================================================================
API_CONFIG = {
    'api_key_env': 'HYPERLIQUID_API_KEY',
    'api_secret_env': 'HYPERLIQUID_API_SECRET',
    'require_auth': True,  # Set to False for read-only mode
}

# =============================================================================
# RISK MANAGEMENT (1X LEVERAGE OPTIMIZED)
# =============================================================================
RISK_CONFIG = {
    # Position sizing (conservative for 1x leverage)
    'max_position_size': 0.05,  # Maximum 5% of portfolio per trade
    'max_total_exposure': 0.15,  # Maximum 15% total portfolio exposure
    
    # Stop loss and take profit (tighter for 1x leverage)
    'default_stop_loss': 0.03,  # 3% default stop loss
    'default_take_profit': 0.10,  # 10% default take profit
    
    # Dynamic risk adjustment
    'volatility_high_threshold': 0.02,  # 2% volatility for high volatility
    'volatility_low_threshold': 0.01,   # 1% volatility for low volatility
    
    # High volatility settings
    'high_vol_stop_loss': 0.05,     # 5% stop loss in high volatility
    'high_vol_take_profit': 0.15,   # 15% take profit in high volatility
    
    # Low volatility settings
    'low_vol_stop_loss': 0.02,      # 2% stop loss in low volatility
    'low_vol_take_profit': 0.08,    # 8% take profit in low volatility
    
    # Maximum daily loss (tighter for 1x leverage)
    'max_daily_loss': 0.03,  # Maximum 3% daily loss
    'max_consecutive_losses': 2,  # Maximum 2 consecutive losses
    
    # Balance protection
    'emergency_stop_balance': 10,  # Stop all trading if balance drops to $10
    'balance_check_interval': 60,  # Check balance every 60 seconds
}

# =============================================================================
# MACD STRATEGY PARAMETERS
# =============================================================================
MACD_CONFIG = {
    'fast_period': 12,  # Fast EMA period
    'slow_period': 26,  # Slow EMA period
    'signal_period': 9,  # Signal line period
    'threshold': 0.0001,  # Minimum MACD threshold for signals
    'confirmation_periods': 3,  # Number of periods to confirm signal
    'multi_timeframe': True,  # Enable multi-timeframe analysis
    'timeframes': ['1m', '5m', '15m', '1h', '4h'],  # Timeframes to analyze
}

# =============================================================================
# AI STRATEGY PARAMETERS
# =============================================================================
AI_CONFIG = {
    'confidence_threshold': 0.65,  # Minimum confidence for signal execution
    'risk_score_threshold': 0.4,   # Maximum risk score for signals
    'correlation_threshold': 0.7,  # Minimum correlation for multi-asset signals
    'sentiment_weight': 0.3,       # Weight for sentiment analysis
    'liquidation_weight': 0.4,     # Weight for liquidation hunting
    'technical_weight': 0.3,       # Weight for technical analysis
    
    # Signal filtering
    'volume_confirmation': True,    # Require volume confirmation
    'trend_strength_filter': True,  # Filter by trend strength
    'signal_validation': True,      # Validate signals before execution
    'min_signals_between_trades': 7,  # Minimum signals between trades
    'signal_cooldown_minutes': 20,    # Cooldown between similar signals
}

# =============================================================================
# LIQUIDATION HUNTING PARAMETERS
# =============================================================================
LIQUIDATION_CONFIG = {
    'enabled': True,  # Enable liquidation hunting
    'min_size_usd': 50000,  # Minimum liquidation size to track ($50k)
    'rebound_window': 300,  # Seconds to analyze rebounds (5 min)
    'min_rebound_pct': 0.02,  # Minimum 2% rebound for signal
    'max_lookback_periods': 100,  # Maximum periods to look back
}

# =============================================================================
# SENTIMENT ANALYSIS PARAMETERS
# =============================================================================
SENTIMENT_CONFIG = {
    'enabled': True,  # Enable sentiment analysis
    'update_interval': 300,  # Update sentiment every 5 minutes
    'sources': ['twitter', 'reddit', 'news'],  # Sentiment sources
    'weight': 0.3,  # Weight in overall signal calculation
    'threshold': 0.6,  # Minimum sentiment threshold
}

# =============================================================================
# CORRELATION ANALYSIS PARAMETERS
# =============================================================================
CORRELATION_CONFIG = {
    'enabled': True,  # Enable correlation analysis
    'correlation_pairs': ['BTC', 'ETH', 'ADA', 'SOL'],  # Assets to correlate with
    'correlation_threshold': 0.7,  # Minimum correlation for signals
    'lookback_periods': 100,  # Periods to calculate correlation
    'update_interval': 600,  # Update correlations every 10 minutes
}

# =============================================================================
# ORDER EXECUTION PARAMETERS
# =============================================================================
ORDER_CONFIG = {
    'default_order_type': 'LIMIT',  # LIMIT, MARKET, STOP_LOSS, TAKE_PROFIT
    'use_reduce_only': True,  # Use reduce-only for closing positions
    
    # Slippage protection (tighter for 1x leverage)
    'max_slippage_pct': 0.05,  # Maximum 0.05% slippage
    'price_buffer_pct': 0.02,  # 0.02% price buffer for orders
    
    # Order management
    'auto_cancel_orders': True,  # Automatically cancel old orders
    'order_timeout_seconds': 300,  # 5 minutes order timeout
    
    # Batch orders
    'enable_batch_orders': False,  # Enable batch order placement
    'max_batch_size': 3,  # Maximum orders in a batch
    
    # Leverage enforcement
    'force_leverage_check': True,  # Always verify leverage is 1x before placing orders
    'leverage_override_warning': True,  # Warn if leverage is not 1x
}

# =============================================================================
# DATA LOGGING PARAMETERS
# =============================================================================
LOGGING_CONFIG = {
    # File paths
    'trades_filename': 'enhanced_bot_trades.csv',
    'signals_filename': 'enhanced_bot_signals.csv',
    'performance_filename': 'enhanced_bot_performance.csv',
    'macd_data_filename': 'enhanced_bot_macd_data.csv',
    'liquidations_filename': 'enhanced_bot_liquidations.csv',
    'balance_log_filename': 'enhanced_bot_balance_log.csv',
    
    # Log levels
    'console_log_level': 'INFO',
    'file_log_level': 'DEBUG',
    
    # Data retention
    'max_csv_rows': 100000,  # Maximum rows in CSV files
    'backup_interval_hours': 24,  # Backup files every 24 hours
}

# =============================================================================
# PERFORMANCE TRACKING PARAMETERS
# =============================================================================
PERFORMANCE_CONFIG = {
    # Metrics to track
    'track_metrics': [
        'total_signals',
        'successful_signals',
        'win_rate',
        'average_win',
        'average_loss',
        'profit_factor',
        'max_drawdown',
        'sharpe_ratio',
        'total_pnl',
        'current_exposure',
        'account_balance',
        'leverage_used'
    ],
    
    # Performance thresholds (adjusted for 1x leverage)
    'min_win_rate': 0.6,  # Minimum 60% win rate
    'min_profit_factor': 1.3,  # Minimum 1.3 profit factor
    'max_drawdown_pct': 0.10,  # Maximum 10% drawdown
    
    # Auto-adjustment
    'auto_adjust_strategy': True,  # Automatically adjust strategy parameters
    'adjustment_threshold': 0.08,   # Adjust after 8% performance drop
}

# =============================================================================
# MARKET CONDITIONS PARAMETERS
# =============================================================================
MARKET_CONFIG = {
    # Bull run detection
    'bull_run_indicators': {
        'price_momentum': 0.02,  # 2% price increase over period
        'volume_increase': 1.5,  # 1.5x volume increase
        'positive_sentiment': 0.6,  # 60% positive sentiment
    },
    
    # Bear market detection
    'bear_market_indicators': {
        'price_decline': -0.02,  # 2% price decline over period
        'volume_decrease': 0.7,  # 30% volume decrease
        'negative_sentiment': 0.6,  # 60% negative sentiment
    },
    
    # Sideways market detection
    'sideways_market_indicators': {
        'price_volatility': 0.01,  # 1% price volatility
        'volume_stability': 0.8,   # 80% volume stability
    }
}

# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================
NOTIFICATION_CONFIG = {
    'enable_notifications': True,
    'notification_types': [
        'high_confidence_signals',
        'large_trades',
        'significant_liquidations',
        'performance_alerts',
        'risk_alerts',
        'order_executions',
        'balance_alerts',
        'leverage_alerts'
    ],
    
    # Notification thresholds
    'large_trade_threshold_usd': 100000,  # $100k+ trades
    'significant_liquidation_usd': 250000,  # $250k+ liquidations
    'performance_alert_threshold': -0.03,  # -3% performance
    'balance_alert_threshold': 15,  # Alert when balance drops below $15
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================
def validate_config():
    """Validate configuration parameters"""
    errors = []
    
    # Check account settings
    if ACCOUNT_CONFIG['balance'] < ACCOUNT_CONFIG['min_balance']:
        errors.append("Account balance cannot be less than minimum balance threshold")
    
    if ACCOUNT_CONFIG['leverage'] > ACCOUNT_CONFIG['max_leverage']:
        errors.append("Leverage cannot exceed maximum allowed leverage")
    
    # Check risk parameters
    if RISK_CONFIG['max_position_size'] > 1.0:
        errors.append("max_position_size cannot exceed 100%")
    
    if RISK_CONFIG['default_stop_loss'] > 1.0:
        errors.append("default_stop_loss cannot exceed 100%")
    
    # Check AI parameters
    if AI_CONFIG['confidence_threshold'] < 0 or AI_CONFIG['confidence_threshold'] > 1:
        errors.append("confidence_threshold must be between 0 and 1")
    
    if AI_CONFIG['risk_score_threshold'] < 0 or AI_CONFIG['risk_score_threshold'] > 1:
        errors.append("risk_score_threshold must be between 0 and 1")
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
    
    return True

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        'exchange': HYPERLIQUID_CONFIG['name'],
        'symbol': HYPERLIQUID_CONFIG['symbol'],
        'account_balance': f"${ACCOUNT_CONFIG['balance']}",
        'min_balance': f"${ACCOUNT_CONFIG['min_balance']}",
        'leverage': f"{ACCOUNT_CONFIG['leverage']}x",
        'risk_level': 'LOW' if ACCOUNT_CONFIG['leverage'] == 1 else 'HIGH',
        'strategy_type': 'CONSERVATIVE' if ACCOUNT_CONFIG['leverage'] == 1 else 'AGGRESSIVE',
        'ai_enabled': True,
        'liquidation_hunting': LIQUIDATION_CONFIG['enabled'],
        'sentiment_analysis': SENTIMENT_CONFIG['enabled'],
        'correlation_analysis': CORRELATION_CONFIG['enabled'],
        'multi_timeframe': MACD_CONFIG['multi_timeframe']
    }

# Validate configuration on import
if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Enhanced AI Bot configuration validation passed!")
        summary = get_config_summary()
        print(f"📊 Configuration Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
else:
    # Validate when imported as module
    validate_config()
