from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
import ema_crossover
import time

# Replace 'your_api_key_here' with your actual NewsAPI key
api_key = 'f5fe5390fbb64c64883b26acdcadc8dc'
base_url = 'https://newsapi.org/v2/everything'

# Replace 'your_telegram_token_here' with your actual Telegram bot token
telegram_token = '7247839345:AAF1YTg3ZTio4n3vQlzgKCn0FexkpneHppI'


def send_signal(update: Update, context: CallbackContext):
    while True:

        signal, close_price, adx, atr = ema_crossover.check_crossover()
        if signal != 'Hold':
            message = f"Symbol: BTCUSDT\nSignal: {signal}\nPrice: {close_price}\nADX: {adx}\nATR: {atr}"
            update.message.reply_text(message)
            result, pnl = ema_crossover.monitor_trade(float(close_price), atr, position_type=signal)
            update.message.reply_text(f'Trade finished successfully\nResult: {result} PNL: {pnl}')

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
