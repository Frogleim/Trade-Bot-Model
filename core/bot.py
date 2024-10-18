from telegram.ext import Updater, CommandHandler, CallbackContext
from binance.client import Client
from telegram import Update
import ema_crossover
import time
import os

client = Client()
telegram_token = os.environ['TELEGRAM_TOKEN']


def send_signal(update: Update, context: CallbackContext):
    while True:
        # try:
        crossover_result = ema_crossover.check_crossover()
        print(crossover_result)

        if crossover_result[0] != 'Hold':
            message = (f"Symbol: BTCUSDT\n⚠️Signal: {crossover_result[0]}\nLong EMA: {crossover_result[5]}\n"
                       f"Short EMA: {crossover_result[6]}\n"
                       f"Price: {crossover_result[1]}\n"
                       f"ADX: {crossover_result[2]}\nATR: {crossover_result[3]}\nRSI: {crossover_result[4]}")
            update.message.reply_text(message)
            current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])
            if crossover_result[0] == 'long':
                result, pnl, close = ema_crossover.long_trade(current_price, crossover_result[3],
                                                             )
                if pnl > 0:
                    pnl_in_diff = close - float(crossover_result[1])
                    update.message.reply_text(f'Trade finished successfully\nResult:🚀 {result} \nPNL: 🤑{pnl_in_diff}\n'
                                              f'Close price: {close}')
                else:
                    pnl_in_diff = float(crossover_result[1]) - close

                    update.message.reply_text(f'Trade was not successful😥\nResult:❌ {result} \nLoss: 🙁{pnl_in_diff}\n'
                                              f'Close price: {close}')
            if crossover_result[0] == 'short':
                result, pnl, close = ema_crossover.short_trade(current_price, crossover_result[3],
                                                             )
                if pnl > 0:
                    pnl_in_diff = float(crossover_result[1]) - close

                    update.message.reply_text(f'Trade finished successfully\nResult:🚀 {result} \nPNL: 🤑{pnl_in_diff}\n'
                                              f'Close price: {close}')
                else:
                    pnl_in_diff = float(crossover_result[1]) - close

                    update.message.reply_text(f'Trade was not successful😥\nResult:❌ {result} \nLoss: 🙁{pnl_in_diff}\n'
                                              f'Close price: {close}')

            time.sleep(60)
        else:
            print("There is no good condition for trade")
            time.sleep(60)




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
