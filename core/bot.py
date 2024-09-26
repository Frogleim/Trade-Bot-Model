from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
import ema_crossover
import time
import pandas as pd
import os

# Replace 'your_api_key_here' with your actual NewsAPI key
telegram_token = '7911524695:AAFPawr8FXJ1gLWAtSQ_jFKj9X_XZuSyKaY'
excel_file = "./trade_results/trade_results.xlsx"


def send_signal(update: Update, context: CallbackContext):
    if not os.path.exists(excel_file):
        df = pd.DataFrame(columns=["Symbol", "Signal", "Price", "ADX", "ATR", "Result", "PNL"])
    else:
        df = pd.read_excel(excel_file)


    while True:

        signal, close_price, adx, atr = ema_crossover.check_crossover()
        if signal != 'Hold':
            message = f"Symbol: BTCUSDT\nSignal: {signal}\nPrice: {close_price}\nADX: {adx}\nATR: {atr}"
            update.message.reply_text(message)
            result, pnl = ema_crossover.monitor_trade(float(close_price), atr, position_type=signal)
            update.message.reply_text(f'Trade finished successfully\nResult: {result} PNL: {pnl}')
            trade_data = {
                "Symbol": "BTCUSDT",
                "Signal": signal,
                "Price": close_price,
                "ADX": adx,
                "ATR": atr,
                "Result": result,
                "PNL": pnl
            }
            df = df.append(trade_data, ignore_index=True)
            df.to_excel(excel_file, index=False, engine='openpyxl')

            time.sleep(60)  # Adjust the sleep interval to check signals (e.g., every minute)
        else:
            update.message.reply_text("There is no good condition for trade")
            time.sleep(5*60)


def start_bot(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'll notify you with trading signals.")
    send_signal(update, context)  # Start sending signals when bot starts


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    # Command to start the bot and begin sending signals
    dp.add_handler(CommandHandler("start", start_bot))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
