import ccxt
import pandas as pd
import pandas_ta as ta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "bot token"

# Initialize the exchange for Binance Futures
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future',  # Use 'future' for futures market
    }
})

# Function to fetch OHLCV data
def fetch_ohlcv(symbol, timeframe, limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)  # Set timestamp as the index
    df.sort_index(inplace=True)  # Sort by timestamp in ascending order
    return df

# Function to calculate VWAP and standard deviation
def calculate_vwap_std(df):
    df["VWAP"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
    df["Std_Dev"] = df["close"].rolling(window=20).std()  # Standard deviation of the last 20 periods
    return df

# Function to check trade conditions
def check_trade_conditions(df):
    latest = df.iloc[-1]
    current_price = latest["close"]
    vwap = latest["VWAP"]
    std_dev = latest["Std_Dev"]

    if current_price < (vwap - std_dev):
        return "up_move", f"Price is below VWAP by more than 1 standard deviation ({std_dev:.2f}), suggesting a potential upward reversal."
    elif current_price > (vwap + std_dev):
        return "down_move", f"Price is above VWAP by more than 1 standard deviation ({std_dev:.2f}), suggesting a potential downward reversal."
    else:
        return None, None

# Function to send alerts
async def send_alert(context: ContextTypes.DEFAULT_TYPE, symbol, timeframe, condition, reason):
    message = f"🚨 Trade Alert ({symbol}, {timeframe}) 🚨\n"
    if condition == "up_move":
        message += "✅ UP MOVE: Price is below VWAP by more than 1 standard deviation.\n"
    elif condition == "down_move":
        message += "✅ DOWN MOVE: Price is above VWAP by more than 1 standard deviation.\n"
    message += f"Reason: {reason}"
    await context.bot.send_message(chat_id=context.job.chat_id, text=message)

# Function to monitor the market
async def monitor_market(context: ContextTypes.DEFAULT_TYPE):
    symbol = "BTC/USDT"  # Change to your trading pair
    timeframes = ["5m", "3m", "1m"]
    for timeframe in timeframes:
        df = fetch_ohlcv(symbol, timeframe)
        df = calculate_vwap_std(df)
        condition, reason = check_trade_conditions(df)
        if condition:
            await send_alert(context, symbol, timeframe, condition, reason)

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bitcoin VWAP Strategy Bot is running! Monitoring the market...")
    # Add the job to the queue
    context.job_queue.run_repeating(monitor_market, interval=60, first=0, chat_id=update.message.chat_id)

# Main function
def main():
    # Build the application with JobQueue enabled
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()





    
