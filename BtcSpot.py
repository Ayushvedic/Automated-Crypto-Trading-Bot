import ccxt
import pandas as pd
import pandas_ta as ta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# Connect to Binance Futures using CCXT
exchange = ccxt.binance({
    'options': {'defaultType': 'future'}
})


# Fetch OHLCV data (candlestick data)
def fetch_data(symbol="BTC/USDT", timeframe="1m", limit=100):
    raw = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


# Add indicators: VWAP and Standard Deviation
def add_indicators(df):
    df["VWAP"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
    df["Std_Dev"] = df["close"].rolling(20).std()  # 20-candle rolling std dev
    return df


# Trading logic – compares price vs VWAP ± Std Dev
def check_trade(df):
    latest = df.iloc[-1]
    price = latest["close"]
    vwap = latest["VWAP"]
    std = latest["Std_Dev"]

    if price < vwap - std:
        return "up", f"Price {price} < VWAP {vwap} - {std:.2f} (possible upward reversal)"
    elif price > vwap + std:
        return "down", f"Price {price} > VWAP {vwap} + {std:.2f} (possible downward reversal)"
    return None, None


# Send alert message to Telegram
async def send_alert(context, symbol, tf, signal, reason):
    msg = f"🚨 Trade Alert ({symbol}, {tf}) 🚨\n"
    if signal == "up":
        msg += "✅ Possible UPWARD move\n"
    else:
        msg += "✅ Possible DOWNWARD move\n"
    msg += f"Reason: {reason}"
    await context.bot.send_message(chat_id=context.job.chat_id, text=msg)


# Monitor one or more timeframes every minute
async def monitor_market(context):
    symbol = "BTC/USDT"
    timeframes = ["1m", "3m", "5m"]

    for tf in timeframes:
        df = fetch_data(symbol, tf)
        df = add_indicators(df)
        signal, reason = check_trade(df)

        if signal:
            await send_alert(context, symbol, tf, signal, reason)


# Start command to trigger monitoring
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 VWAP Trading Bot started! Monitoring BTC/USDT...")
    context.job_queue.run_repeating(monitor_market, interval=60, first=0, chat_id=update.message.chat_id)


# Main runner
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()


