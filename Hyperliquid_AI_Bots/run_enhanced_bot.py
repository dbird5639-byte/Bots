#!/usr/bin/env python3
"""
Enhanced AI XRP Bot Launcher

This script launches the enhanced AI-powered XRP trading bot
that integrates multiple AI trading strategies.
"""

import asyncio
import sys
import os
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🚀 ENHANCED AI XRP TRADING BOT")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Exchange: Hyperliquid")
    print(f"Symbol: XRP")
    print(f"AI Strategies: Liquidation Hunting, Sentiment Analysis, Correlation Trading")
    print("=" * 70)

def print_features():
    """Print bot features"""
    print("\n🧠 AI-Powered Features:")
    print("   • Liquidation Hunting with Rebound Analysis")
    print("   • Real-time Sentiment Analysis")
    print("   • Multi-Asset Correlation Trading")
    print("   • Dynamic Risk Management")
    print("   • Portfolio Optimization")
    print("   • Multi-Timeframe Analysis")
    
    print("\n🛡️ Risk Management:")
    print("   • 1x Leverage Only")
    print("   • Dynamic Position Sizing")
    print("   • Real-time Balance Monitoring")
    print("   • Emergency Stop Capabilities")
    
    print("\n📊 Performance Tracking:")
    print("   • Multi-Strategy Performance Metrics")
    print("   • Real-time P&L Monitoring")
    print("   • Risk-Adjusted Returns")
    print("   • Strategy Correlation Analysis")

def main():
    """Main launcher function"""
    try:
        print_banner()
        print_features()
        
        print("\n🚀 Launching Enhanced AI XRP Bot...")
        print("   Press Ctrl+C to stop the bot")
        print("   Check logs for detailed information")
        
        # Import and run the bot
        try:
            from enhanced_xrp_bot import EnhancedXRPBot
            
            async def run_bot():
                bot = EnhancedXRPBot()
                await bot.start_bot()
            
            asyncio.run(run_bot())
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Make sure enhanced_xrp_bot.py exists in the same directory")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
