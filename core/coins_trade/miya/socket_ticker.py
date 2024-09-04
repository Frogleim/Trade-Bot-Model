from datetime import datetime, timedelta
import websocket
import threading
import json
from . import logging_settings


class PriceStreaming(websocket.WebSocketApp):
    def __init__(self, url):
        self.latest_price = None
        self.lock = threading.Lock()
        super().__init__(url=url, on_open=self.on_open, on_message=self.on_message,
                         on_error=self.on_error, on_close=self.on_close)
        self.run_forever()

    def on_open(self):
        logging_settings.system_log.warning('Price ticker open')

    def on_message(self, ws, msg):
        data = json.loads(msg)
        self.proccess_message(data)

    def on_error(self, ws, e):
        logging_settings.error_logs_logger.error('Websocket Error', e)

    def on_close(self, ws):
        logging_settings.system_log.info('Closing')

    def proccess_message(self, data):
        price = data['p']
        with self.lock:
            self.latest_price = price
        print(price)

    def get_latest_price(self):
        with self.lock:
            return self.latest_price


if __name__ == '__main__':
    price_stream = PriceStreaming('wss://fstream.binance.com/ws/maticusdt@markPrice')
    threading.Thread(target=price_stream).start()

    # Example of how to get the latest price from another part of the code
    import time

    while True:
        latest_price = price_stream.get_latest_price()
        if latest_price is not None:
            print(f"Latest Price: {latest_price}")
        time.sleep(1)
