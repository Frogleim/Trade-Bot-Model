import logging
import os
import random
import time
from pyrogram import Client, filters, types
from core import bitcoin_ticker, make_trades, logs_handler, config

PROXY = os.getenv("PROXY")
TOKEN = os.getenv("TOKEN")
APP_ID = os.getenv("APP_ID")
APP_HASH = os.getenv("APP_HASH")

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "sessions")
body = None
btc_price_change = False
logging.basicConfig(filename=f'{files_dir}/logs/bot_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BotClient:
    def __init__(self):
        self.token = config.TOKEN
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    def create_app(self):
        with Client(f'trade_bots', self.api_id, self.api_hash, self.token) as client:
            return client


bot_app = BotClient()
app = bot_app.create_app()
service_count = 0


@app.on_message(filters.command(["start"]))
async def start_handler(client: "Client", message: "types.Message"):
    global body, btc_price_change
    chat_id = -4045954741
    await client.send_message(chat_id, 'Oracle Starting!')
    while True:
        btc_price_change, opened_price = make_trades.check_price_changes()
        if btc_price_change:
            bitcoin_ticker.create_order(side='long')
            body = f'Buying ETHUSDT for price {round(float(opened_price), 1)}'
            logging.info(body)
            await client.send_message(chat_id, text=body)
            while True:
                res = make_trades.pnl_long(opened_price=opened_price)
                if res == 'Profit':
                    logging.info('Position closed')
                    log = logs_handler.read_logs_txt()
                    trade_log = ''.join(log)
                    await client.send_message(chat_id, text=trade_log)
                    break
                elif res == 'Loss':
                    logging.info('Position closed')
                    log = logs_handler.read_logs_txt()
                    trade_log = ''.join(log)
                    await client.send_message(chat_id, text=trade_log)
                    break
                time.sleep(random.uniform(0.6587, 1.11))
        else:
            bitcoin_ticker.create_order(side='short')
            body = f'Selling ETHUSDT for price {round(float(opened_price), 1)}'
            logging.info(body)
            await client.send_message(chat_id, text=body)
            while True:
                res = make_trades.pnl_short(opened_price=opened_price)
                if res == 'Profit':
                    logging.info('Position closed')
                    log = logs_handler.read_logs_txt()
                    trade_log = ''.join(log)
                    await client.send_message(chat_id, text=trade_log)
                    break
                elif res == 'Loss':
                    logging.info('Position closed')
                    log = logs_handler.read_logs_txt()
                    trade_log = ''.join(log)
                    await client.send_message(chat_id, text=trade_log)
                    break
                time.sleep(random.uniform(0.6587, 1.11))
            time.sleep(10)


if __name__ == '__main__':
    app.run()
