from datetime import datetime, timedelta
import websocket
import threading
import json
import psycopg2
import db

class Streaming(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def on_message(self, ws, msg):
        data = json.loads(msg)
        self.process_message(data)

    def on_error(self, ws, e):
        print('Error', e)

    def on_close(self, ws):
        print('Closing')

    def process_message(self, data):
        my_db = db.DataBase()

class StreamingDepthBook(websocket.WebSocketApp):
    def __init__(self, url, bid_ask_threshold=1.1):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')
        self.total_bids = 0
        self.total_asks = 0
        self.bid_ask_threshold = bid_ask_threshold
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        data = json.loads(msg)
        if 'b' in data and 'a' in data:
            bids = data['b']
            asks = data['a']
            total_bids_quantity = sum(float(bid[1]) for bid in bids)
            total_asks_quantity = sum(float(ask[1]) for ask in asks)

            # Determine imbalance based on threshold
            if total_bids_quantity > self.bid_ask_threshold * total_asks_quantity:
                print("Strong buying pressure (bullish)")
            elif total_asks_quantity > self.bid_ask_threshold * total_bids_quantity:
                print("Strong selling pressure (bearish)")
            else:
                print("Market is balanced")

class ForcedOrders(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')
        self.forced_orders = []
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        data = json.loads(msg)
        if data.get('e') == 'forceOrder':
            self.forced_orders.append(data)
            self.algorithmic_trading()

    def algorithmic_trading(self):
        frequency = len(self.forced_orders)
        severity = sum(float(order['o']['q']) for order in self.forced_orders)
        print(f"Frequency of forced liquidations: {frequency}")
        print(f"Total severity of forced liquidations: {severity}")

if __name__ == '__main__':
    threading.Thread(target=Streaming, args=('wss://fstream.binance.com/ws/maticusdt@aggTrade',)).start()
    threading.Thread(target=StreamingDepthBook, args=('wss://fstream.binance.com/ws/maticusdt@depth', 1.1)).start()
    threading.Thread(target=ForcedOrders, args=('wss://fstream.binance.com/ws/maticusdt@forceOrder',)).start()
