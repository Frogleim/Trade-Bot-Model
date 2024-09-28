from telegram.ext import Updater, CommandHandler, CallbackContext

from telegram import Update
from binance.client import Client
import ema_crossover
import time
import pandas as pd
import os

client = Client()
# Replace 'your_api_key_here' with your actual NewsAPI key
telegram_token = '7911524695:AAFPawr8FXJ1gLWAtSQ_jFKj9X_XZuSyKaY'


def send_signal(update: Update, context: CallbackContext):
    while True:
        try:
            # Check if the function returns a valid result
            crossover_result = ema_crossover.check_crossover()

            if crossover_result is not None:
                # Unpack values if the result is valid
                signal, close_price, adx, atr = crossover_result

                if signal != 'Hold':
                    message = f"Symbol: BTCUSDT\n⚠️Signal: {signal}\nPrice: {close_price}\nADX: {adx}\nATR: {atr}"
                    update.message.reply_text(message)

                    # Fetch current price
                    current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])

                    # Monitor the trade
                    result, pnl, close = ema_crossover.monitor_trade(current_price, atr, position_type=signal)
                    if pnl > 0:
                        update.message.reply_text(f'Trade finished successfully\nResult:🚀 {result} \nPNL: 🤑{pnl}\n'
                                                  f'Close price: {close}')
                    else:
                        update.message.reply_text(f'Trade was not successful😥\nResult:❌ {result} \nLoss: 🙁{pnl}\n'
                                                  f'Close price: {close}')

                    time.sleep(60)  # Adjust the sleep interval to check signals (e.g., every minute)
                else:
                    print("There is no good condition for trade")
                    time.sleep(5 * 60)
            else:
                # Handle the case where the function returns None
                update.message.reply_text("⚠️ Unable to retrieve crossover data. Skipping this check.")
                time.sleep(5 * 60)

        except ValueError as ve:
            # If specific data is missing, notify which data is missing
            update.message.reply_text(f"⚠️ Data issue: {ve}")
            print(f"Data issue: {ve}")
            time.sleep(5 * 60)
        except Exception as e:
            # Catch and notify other general errors
            print(f"Error: {e}")
            update.message.reply_text(f'⛔️Bot is down! Error message: {e}')
            break



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
