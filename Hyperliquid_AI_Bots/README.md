# 🚀 Enhanced AI Trading Bots for Hyperliquid

This directory contains enhanced AI-powered trading bots for Hyperliquid, built on the wisdom of Jacob Amaral and Kevin Davy. These bots integrate multiple AI trading strategies with advanced risk management optimized for 1x leverage trading.

## 🎯 What These Bots Do

### **Enhanced XRP AI Bot** 🧠
- **Multi-Strategy Signal Generation**: Combines liquidation hunting, sentiment analysis, correlation trading, and technical analysis
- **AI-Powered Risk Management**: Dynamic position sizing and risk assessment
- **Real-Time Market Analysis**: Continuous monitoring of market conditions
- **Portfolio Optimization**: AI-driven position management and rebalancing

### **Enhanced MACD Bot** 📊
- **Multi-Timeframe MACD Analysis**: Analyzes MACD across multiple timeframes (1m, 5m, 15m, 1h, 4h)
- **Advanced Signal Filtering**: AI-powered signal validation and filtering
- **Volume Confirmation**: Requires volume confirmation for signal execution
- **Trend Strength Analysis**: Filters signals based on trend strength

### **Key Features** ✨
- **1x Leverage Only**: No margin trading, conservative risk management
- **Balance Protection**: Stops trading if balance drops below $10
- **Multi-Strategy Integration**: Combines multiple AI approaches
- **Real-Time Performance Monitoring**: Continuous tracking of bot performance
- **Emergency Stop Capabilities**: Automatic shutdown on risk violations

## 🚀 Quick Start

### 1. **Get Hyperliquid API Credentials**
```bash
# Visit Hyperliquid and create account
# https://app.hyperliquid.xyz/

# Generate API keys with trading permissions
# Set environment variables:
export HYPERLIQUID_API_KEY='your_api_key'
export HYPERLIQUID_API_SECRET='your_api_secret'
```

### 2. **Install Dependencies**
```bash
cd Backtesting/bots
pip install -r requirements.txt
```

### 3. **Run the Enhanced Bots**
```bash
# Run Enhanced XRP AI Bot
cd Bots/Hyperliquid_AI_Bots
python run_enhanced_bot.py

# Run Enhanced MACD Bot (when implemented)
python enhanced_macd_bot.py
```

## 📁 File Structure

```
Hyperliquid_AI_Bots/
├── config.py                    # Centralized configuration for all bots
├── run_enhanced_bot.py          # Launcher for enhanced XRP AI bot
├── enhanced_xrp_bot.py          # Enhanced XRP AI bot (to be created)
├── enhanced_macd_bot.py         # Enhanced MACD bot (to be created)
├── README.md                    # This file
├── enhanced_bot_trades.csv      # Trade data logs
├── enhanced_bot_signals.csv     # Generated signal logs
├── enhanced_bot_performance.csv # Performance tracking logs
└── enhanced_bot_balance_log.csv # Balance monitoring logs
```

## ⚙️ Configuration

All bot parameters are configurable in `config.py`:

### **Account & Leverage Settings**
```python
ACCOUNT_CONFIG = {
    'balance': 60,              # Your $60 balance
    'min_balance': 10,          # Stop trading if below $10
    'leverage': 1,              # 1x leverage (no leverage)
    'max_leverage': 1,          # Maximum allowed leverage
}
```

### **Risk Management (1x Leverage Optimized)**
```python
RISK_CONFIG = {
    'max_position_size': 0.05,  # Max 5% per trade (reduced from 10%)
    'max_total_exposure': 0.15, # Max 15% total exposure (reduced from 30%)
    'default_stop_loss': 0.03,  # 3% stop loss (reduced from 5%)
    'default_take_profit': 0.10, # 10% take profit (reduced from 15%)
    'max_daily_loss': 0.03,     # 3% max daily loss (reduced from 5%)
    'emergency_stop_balance': 10, # Stop all trading if balance drops to $10
}
```

### **AI Strategy Parameters**
```python
AI_CONFIG = {
    'confidence_threshold': 0.65,    # Minimum 65% confidence for signals
    'risk_score_threshold': 0.4,     # Maximum 40% risk score
    'volume_confirmation': True,      # Require volume confirmation
    'trend_strength_filter': True,   # Filter by trend strength
    'signal_validation': True,        # Validate signals before execution
}
```

### **MACD Strategy Parameters**
```python
MACD_CONFIG = {
    'fast_period': 12,          # Fast EMA period
    'slow_period': 26,          # Slow EMA period
    'signal_period': 9,         # Signal line period
    'multi_timeframe': True,    # Enable multi-timeframe analysis
    'timeframes': ['1m', '5m', '15m', '1h', '4h']
}
```

## 🔍 Strategy Logic

### **1. Multi-Strategy Signal Generation**
- **Liquidation Hunting**: Detects large liquidations and generates rebound signals
- **Sentiment Analysis**: Analyzes market sentiment from multiple sources
- **Correlation Trading**: Identifies correlation opportunities with other assets
- **Technical Analysis**: RSI, MACD, volume analysis, and trend following

### **2. AI-Powered Risk Management**
- **Dynamic Position Sizing**: Adjusts based on confidence and risk scores
- **Real-Time Balance Monitoring**: Continuous balance checking every 60 seconds
- **Emergency Stop**: Automatic shutdown on balance violations
- **Risk Score Calculation**: AI-driven risk assessment for each signal

### **3. Signal Validation & Filtering**
- **Confidence Thresholds**: Minimum 65% confidence required
- **Volume Confirmation**: Requires volume confirmation for execution
- **Trend Strength Filter**: Filters signals based on trend strength
- **Signal Cooldown**: Prevents signal spam with cooldown periods

### **4. Multi-Timeframe Analysis**
- **Timeframe Integration**: Combines signals from multiple timeframes
- **Signal Weighting**: Weights signals based on timeframe importance
- **Confirmation Logic**: Requires confirmation across timeframes
- **Trend Alignment**: Ensures signals align with overall trend

## 📊 Signal Types

| Signal Type | Description | Confidence | Action | Source |
|-------------|-------------|------------|---------|---------|
| `MACD_BULLISH` | MACD bullish crossover | 70%+ | BUY | MACD Analysis |
| `MACD_BEARISH` | MACD bearish crossover | 70%+ | SELL | MACD Analysis |
| `LIQUIDATION_REBOUND` | Price rebound after liquidation | 90% | BUY | Liquidation Hunting |
| `SENTIMENT_BULLISH` | Positive sentiment detected | 65% | BUY | Sentiment Analysis |
| `CORRELATION_SIGNAL` | Correlation opportunity | 60% | BUY/SELL | Correlation Analysis |
| `TREND_FOLLOWING` | Strong trend detected | 60% | BUY/SELL | Trend Analysis |
| `VOLUME_SPIKE` | Unusual volume activity | 55% | BUY/SELL | Volume Analysis |

## 🎮 Usage Examples

### **Basic Usage**
```bash
# Start the enhanced AI bot
python run_enhanced_bot.py

# Stop with Ctrl+C
```

### **Configuration Changes**
```python
# Edit config.py
ACCOUNT_CONFIG['balance'] = 100        # Change balance to $100
RISK_CONFIG['max_position_size'] = 0.03 # Reduce position size to 3%
AI_CONFIG['confidence_threshold'] = 0.7 # Increase confidence threshold to 70%
```

### **Custom Parameters**
```python
# Adjust AI strategy weights
AI_CONFIG['liquidation_weight'] = 0.5    # Increase liquidation hunting weight
AI_CONFIG['sentiment_weight'] = 0.4      # Increase sentiment analysis weight
AI_CONFIG['technical_weight'] = 0.1      # Decrease technical analysis weight

# Adjust risk parameters
RISK_CONFIG['max_daily_loss'] = 0.02     # Tighter daily loss limit (2%)
RISK_CONFIG['default_stop_loss'] = 0.02  # Tighter stop loss (2%)
```

## 📈 Performance Tracking

The bots automatically track:

- **Multi-Strategy Performance**: Individual performance for each strategy
- **Risk Metrics**: Real-time risk assessment and monitoring
- **Balance Protection**: Continuous balance monitoring and alerts
- **Signal Quality**: Success rates and confidence analysis
- **Portfolio Optimization**: Position sizing and exposure management

### **Performance Metrics**
- Win Rate (target: 60%+)
- Profit Factor (target: 1.3+)
- Maximum Drawdown (limit: 10%)
- Sharpe Ratio
- Total P&L
- Risk-Adjusted Returns

## 🚨 Risk Warnings

### **⚠️ Important Disclaimers**
1. **This is NOT financial advice**
2. **Past performance doesn't guarantee future results**
3. **Cryptocurrency trading is highly risky**
4. **Only trade with money you can afford to lose**
5. **Hyperliquid is a decentralized exchange - understand the risks**

### **🔒 Risk Management Features**
- **1x Leverage Only**: No margin trading
- **Automatic Position Sizing**: Conservative position sizing
- **Dynamic Stop Losses**: Adaptive risk management
- **Balance Protection**: Emergency stop at $10 balance
- **Performance Monitoring**: Continuous risk assessment
- **Emergency Shutdown**: Automatic stop on violations

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. API Connection Errors**
```bash
# Check internet connection
ping api.hyperliquid.xyz

# Verify API credentials
echo $HYPERLIQUID_API_KEY
echo $HYPERLIQUID_API_SECRET

# Check Hyperliquid status
# https://status.hyperliquid.xyz/
```

#### **2. No Signals Generated**
- Check confidence thresholds in config.py
- Verify data stream connections
- Monitor console for error messages
- Check minimum trade size thresholds

#### **3. Risk Management Issues**
- Verify balance settings
- Check leverage enforcement
- Monitor emergency stop triggers
- Review risk parameter settings

### **Debug Mode**
```python
# Enable debug logging in config.py
LOGGING_CONFIG['console_log_level'] = 'DEBUG'
LOGGING_CONFIG['file_log_level'] = 'DEBUG'
```

## 🔮 Future Enhancements

### **Planned Features**
- [ ] Machine learning price predictions
- [ ] Advanced sentiment analysis
- [ ] Portfolio optimization algorithms
- [ ] Backtesting integration
- [ ] Web dashboard interface
- [ ] Mobile notifications
- [ ] Strategy backtesting framework

### **Customization Options**
- [ ] Add new AI strategies
- [ ] Custom signal types
- [ ] Alternative data sources
- [ ] Risk management rules
- [ ] Performance metrics
- [ ] Order execution strategies

## 📚 Learning Resources

### **Strategy Concepts**
- [Trading Strategy Development](https://www.investopedia.com/trading/developing-trading-strategies-4689657)
- [Risk Management in Trading](https://www.investopedia.com/articles/trading/09/risk-management-trading.asp)
- [Technical Analysis](https://www.investopedia.com/technical-analysis-4689657)

### **AI Trading Resources**
- [Machine Learning for Trading](https://www.investopedia.com/articles/active-trading/041114/machine-learning-trading-basics.asp)
- [Algorithmic Trading Strategies](https://www.investopedia.com/articles/active-trading/092114/algorithmic-trading-strategies-beginners-guide.asp)

### **Hyperliquid-Specific**
- [Hyperliquid Documentation](https://hyperliquid.gitbook.io/hyperliquid/)
- [Hyperliquid API Reference](https://hyperliquid.gitbook.io/hyperliquid/api-reference)
- [Hyperliquid App](https://app.hyperliquid.xyz/)

## 🤝 Support & Community

### **Getting Help**
1. Check the logs for error messages
2. Review configuration parameters
3. Test with smaller thresholds first
4. Monitor system resources
5. Check Hyperliquid status page

### **Contributing**
- Report bugs and issues
- Suggest new features
- Share strategy improvements
- Contribute to documentation

## 📄 License

This project is for educational and research purposes. Use at your own risk.

---

**🚀 Ready to start AI-powered trading on Hyperliquid? Run `python run_enhanced_bot.py` and watch the AI bots trade!**

**Remember: Start small, test thoroughly, and always manage your risk!**

**Built on the wisdom of Jacob Amaral and Kevin Davy - Quality over quantity!**
