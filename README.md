# Automated-Crypto-Trading-Bot 📈🤖
This bot automatically monitors Bitcoin (BTC/USDT) on Binance Futures and sends real-time trade alerts to your Telegram.

Features:
Fetches OHLCV data via CCXT.

Calculates VWAP and 20-period rolling standard deviation.

Detects upward or downward reversal signals based on price deviation.

Monitors multiple timeframes (1m, 3m, 5m).

Pushes alerts directly to Telegram using Telegram Bot API.

How It Works:
Bot fetches candlestick data.

Applies VWAP + Std Dev strategy.

If signal detected → Sends message to Telegram.

Runs continuously with automatic scheduling.
