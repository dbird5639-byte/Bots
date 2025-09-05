# Order Flow Imbalance (OFI) Trading Bot

A sophisticated trading bot that analyzes order flow imbalances to identify profitable trading opportunities in real-time markets.

## 🎯 Overview

The Order Flow Imbalance (OFI) Trading Bot is designed to detect and capitalize on market inefficiencies by analyzing the relationship between buy and sell orders. This bot identifies when there's a significant imbalance in order flow, which often precedes price movements.

## 🔍 How It Works

### Order Flow Analysis
- **Bid-Ask Spread Monitoring**: Tracks the spread between highest bid and lowest ask
- **Volume Imbalance Detection**: Identifies when buy/sell volume is significantly skewed
- **Order Book Depth Analysis**: Monitors the depth of market orders
- **Real-time Data Processing**: Processes market data with minimal latency

### Trading Signals
- **Buy Signal**: When buy orders significantly outweigh sell orders
- **Sell Signal**: When sell orders significantly outweigh buy orders
- **Position Sizing**: Dynamic position sizing based on imbalance strength
- **Risk Management**: Built-in stop-loss and take-profit mechanisms

## 🚀 Features

- **Multi-level Order Flow Analysis**: Analyzes multiple timeframes and order book levels
- **Real-time Market Data**: Connects to major exchanges via WebSocket APIs
- **Advanced Risk Management**: Position sizing, stop-losses, and portfolio protection
- **Performance Analytics**: Comprehensive backtesting and live performance metrics
- **Configurable Parameters**: Easily adjustable strategy parameters

## 📊 Performance Metrics

The bot tracks various performance indicators:
- Win Rate: Percentage of profitable trades
- Sharpe Ratio: Risk-adjusted returns
- Maximum Drawdown: Largest peak-to-trough decline
- Profit Factor: Ratio of gross profit to gross loss
- Average Trade Duration: Time between entry and exit

## 🛠️ Technical Requirements

### Prerequisites
- Python 3.8+
- WebSocket-capable internet connection
- Exchange API access (with appropriate permissions)

### Dependencies
- `websockets` - Real-time data streaming
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `ccxt` - Exchange API integration
- `matplotlib` - Performance visualization

## 📁 Project Structure

```
01_OFI_Trading_Bot/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config/
│   ├── config.yaml          # Main configuration file
│   └── exchanges.yaml       # Exchange-specific settings
├── src/
│   ├── __init__.py
│   ├── main.py              # Main bot entry point
│   ├── ofi_analyzer.py      # Order flow analysis engine
│   ├── signal_generator.py  # Trading signal generation
│   ├── risk_manager.py      # Risk management system
│   ├── exchange_connector.py # Exchange API integration
│   └── utils/
│       ├── __init__.py
│       ├── data_processor.py # Market data processing
│       └── logger.py        # Logging utilities
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py     # Base strategy class
│   └── ofi_strategy.py      # OFI-specific strategy
├── tests/
│   ├── __init__.py
│   ├── test_ofi_analyzer.py
│   └── test_strategy.py
├── data/
│   └── historical/          # Historical data storage
├── logs/                    # Bot operation logs
├── results/                 # Backtesting results
└── docs/                    # Additional documentation
```

## 🚀 Quick Start

### 1. Installation
```bash
cd 01_OFI_Trading_Bot
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your exchange API keys and preferences
```

### 3. Run the Bot
```bash
python src/main.py
```

## ⚙️ Configuration

### Basic Settings
```yaml
# config/config.yaml
bot:
  name: "OFI Trading Bot"
  version: "1.0.0"
  mode: "live"  # live, paper, backtest

exchanges:
  - name: "binance"
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    testnet: false

strategy:
  ofi_threshold: 0.6        # Minimum imbalance ratio
  position_size: 0.1        # Percentage of portfolio per trade
  max_positions: 3          # Maximum concurrent positions
  
risk_management:
  stop_loss: 0.02           # 2% stop loss
  take_profit: 0.04         # 4% take profit
  max_drawdown: 0.15        # 15% maximum drawdown
```

## 📈 Strategy Parameters

### OFI Thresholds
- **Low Imbalance**: 0.3-0.5 (conservative)
- **Medium Imbalance**: 0.5-0.7 (balanced)
- **High Imbalance**: 0.7+ (aggressive)

### Timeframes
- **Short-term**: 1-5 minute imbalances
- **Medium-term**: 15-30 minute imbalances
- **Long-term**: 1-4 hour imbalances

## 🔒 Risk Management

### Position Sizing
- **Conservative**: 1-2% of portfolio per trade
- **Moderate**: 3-5% of portfolio per trade
- **Aggressive**: 5-10% of portfolio per trade

### Stop Loss Strategies
- **Fixed Percentage**: Set percentage from entry
- **Trailing Stop**: Dynamic stop that follows price
- **ATR-based**: Based on Average True Range

## 📊 Backtesting

### Historical Data Requirements
- **Minimum Period**: 6 months of historical data
- **Data Granularity**: 1-minute OHLCV data
- **Market Coverage**: Multiple market conditions

### Performance Metrics
- **Total Return**: Overall profitability
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest loss period
- **Win Rate**: Percentage of winning trades

## 🚨 Important Considerations

### Market Conditions
- **High Volatility**: May generate false signals
- **Low Liquidity**: Can impact execution quality
- **News Events**: May override technical signals

### Technical Limitations
- **API Rate Limits**: Exchange-specific restrictions
- **Network Latency**: Affects signal timing
- **Data Quality**: Garbage in, garbage out

## 🔧 Customization

### Strategy Modifications
- Adjust OFI thresholds based on market conditions
- Implement additional filters (volume, volatility)
- Add machine learning components for signal enhancement

### Risk Management
- Customize position sizing algorithms
- Implement dynamic stop-loss strategies
- Add portfolio-level risk controls

## 📚 Additional Resources

- [Order Flow Analysis Guide](docs/order-flow-analysis.md)
- [Risk Management Best Practices](docs/risk-management.md)
- [Exchange API Integration](docs/exchange-integration.md)
- [Performance Optimization](docs/optimization.md)

## ⚠️ Disclaimer

This trading bot is for educational purposes only. Trading cryptocurrencies involves significant risk and can result in substantial financial losses. Always:
- Test thoroughly on paper trading first
- Start with small amounts
- Understand the risks involved
- Never invest more than you can afford to lose

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the trading community**
