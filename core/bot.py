from telegram.ext import Updater, CommandHandler, CallbackContext
from binance.client import Client
from telegram import Update
import app
from socket_binance import get_wallet
import time
import os

client = Client()
telegram_token = os.environ['TELEGRAM_TOKEN']


def send_signal(update: Update, context: CallbackContext):
    while True:
        # try:
        crossover_result = app.check_crossover()
        print(crossover_result)

        if crossover_result[0] != 'Hold':
            message = (f"Symbol: BTCUSDT\n⚠️Signal: {crossover_result[0]}\nLong EMA: {crossover_result[5]}\n"
                       f"Short EMA: {crossover_result[6]}\n"
                       f"Price: {crossover_result[1]}\n"
                       f"ADX: {crossover_result[2]}\nATR: {crossover_result[3]}\nRSI: {crossover_result[4]}")
            update.message.reply_text(message)
            current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])
            if crossover_result[0] == 'long':
                result, pnl, close = app.long_trade(current_price, crossover_result[3],
                                                             )
                if pnl > 0:
                    avail_balance = get_wallet()
                    pnl_in_diff = close - float(crossover_result[1])
                    update.message.reply_text(f'Trade finished successfully\n'
                                              f'Result:🚀 {result} \nPNL: 🤑{pnl_in_diff}\n'
                                              f'Close price: {close}\n💲{avail_balance}')
                else:
                    avail_balance = get_wallet()
                    pnl_in_diff = float(crossover_result[1]) - close
                    update.message.reply_text(f'Trade was not successful😥\n'
                                              f'Result:❌ {result} \nLoss: 🙁{pnl_in_diff}\n'
                                              f'Close price: {close}\n💲{avail_balance}')
            if crossover_result[0] == 'short':
                result, pnl, close = app.short_trade(current_price, crossover_result[3],
                                                             )
                if pnl > 0:
                    avail_balance = get_wallet()
                    pnl_in_diff = float(crossover_result[1]) - close
                    update.message.reply_text(f'Trade finished successfully\n'
                                              f'Result:🚀 {result} \nPNL: 🤑{pnl_in_diff}\n'
                                              f'Close price: {close}\n💲{avail_balance}')
                else:
                    avail_balance = get_wallet()
                    pnl_in_diff = float(crossover_result[1]) - close
                    update.message.reply_text(f'Trade was not successful😥\n'
                                              f'Result:❌ {result} \nLoss: 🙁{pnl_in_diff}\n'
                                              f'Close price: {close}\n💲{avail_balance}')

            time.sleep(60)
        else:
            print("There is no good condition for trade")
            time.sleep(60)




def start_bot(update: Update, context: CallbackContext):
    avail_balance = get_wallet()
    update.message.reply_text(f"Hello, I'm Miya Trade bot! I'll notify you with trading signals.\n"
                              f"Binance Futures Wallet:💲{avail_balance}")
    send_signal(update, context)


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_bot))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
