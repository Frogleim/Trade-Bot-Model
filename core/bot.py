import os
from dotenv import load_dotenv
from binance.client import Client
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import app
from util import search_signal
from core.util.socket_binance import get_wallet
from core.util.db import insert_history
import logging
import time

# Load environment variables
load_dotenv(dotenv_path='.env')
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
telegram_token = os.getenv('TELEGRAM_TOKEN', '7247839345:AAF1YTg3ZTio4n3vQlzgKCn0FexkpneHppI')

client = Client(api_key, api_secret)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

cryptos = ["btcusdt", "ethusdt", "bnbusdt", "adausdt", "xrpusdt"]

# Function to monitor the trade after placing it
def monitor_trade(update: Update, context: CallbackContext, symbol: str, entry_price: float, side: str):
    chat_id = update.effective_chat.id
    update.message.reply_text(f"Monitoring {side} trade for {symbol.upper()}...")

    while True:
        current_price = float(client.futures_ticker(symbol=symbol.upper())['lastPrice'])

        # Example: Exit when profit/loss threshold reached (customize these thresholds)
        if side == "Long" and current_price >= entry_price * 1.004:  # 1% profit target
            result = "Take Profit"
            break
        elif side == "Long" and current_price <= entry_price * 0.997:  # 1% loss
            result = "Stop Loss"
            break
        elif side == "Short" and current_price <= entry_price * 0.997:
            result = "Take Profit"
            break
        elif side == "Short" and current_price >= entry_price * 1.004:
            result = "Stop Loss"
            break

        time.sleep(10)  # Check every 10 seconds

    # Close the trade and send results
    close_price = current_price
    pnl_in_diff = abs(close_price - entry_price)
    avail_balance = get_wallet()
    message = (f"Trade finished\nResult: 🚀 {result}\nPNL: {'🤑' if result == 'Take Profit' else '🙁'} {pnl_in_diff}\n"
               f"Close price: {close_price}\n💲Balance: {avail_balance}")
    context.bot.send_message(chat_id=chat_id, text=message)

    insert_history(symbol=symbol.upper(), entry_price=entry_price, close_price=close_price, pnl=pnl_in_diff, side=side)
    update.message.reply_text(f"Resuming signal scanning for {symbol.upper()}.")

    # Resume scanning signals for the symbol
    context.job_queue.run_repeating(send_trade_signal, interval=60 * 5, first=1,
                                    context={'symbol': symbol, 'chat_id': chat_id})

# Function to send trade signals
def send_trade_signal(context: CallbackContext):
    job_data = context.job.context
    symbol = job_data['symbol']
    chat_id = job_data['chat_id']
    signal = search_signal.process_signals(symbol=symbol, interval='5m')

    if signal[0] != 'Hold':
        current_price = float(client.futures_ticker(symbol=symbol.upper())['lastPrice'])
        message = (f"Symbol: {symbol.upper()}\n⚠️Signal: {signal[0]}\n"
                   f"Price: {current_price}\n"
                   f"Support: {signal[2]}\n"
                   f"Resistance: {signal[3]}\n")
        context.bot.send_message(chat_id=chat_id, text=message)

        # Stop the current signal scanning job
        context.job.schedule_removal()

        # Place the trade and start monitoring
        # if signal[0] == 'Long':
        #     result, pnl, entry_price = app.long_trade(current_price, signal[3])
        # else:
        #     result, pnl, entry_price = app.short_trade(current_price, signal[2])

        monitor_trade(context.job.context['update'], context, symbol, current_price, signal[0])

    else:
        logger.info(f"No good condition for trade on {symbol.upper()}.")

# Function to start the bot and schedule periodic updates
def start_bot(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text(f"Hello! I'm Miya Trade bot! I will notify you with trading signals for {cryptos}.\n")

    # Add jobs for each symbol
    for symbol in cryptos:
        context.job_queue.run_repeating(send_trade_signal, interval=60 * 5, first=1,
                                        context={'symbol': symbol, 'chat_id': chat_id, 'update': update})

def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_bot))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
