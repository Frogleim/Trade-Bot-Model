import time
# from . import config, bitcoin_ticker
import crypto_ticker
from binance.client import Client
import config


start_time = time.time()
client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET)

# TODO add previous price calculator method, fix pnl algorythm, run on docker, starting to build neural network
# TODO Algorithm final view. Predict price according by price differences and last "Price Close"

btc_current_class = bitcoin_ticker.LivePrice()
btc_current = btc_current_class.get_live_price()
end_time = time.time()
total_time = end_time - start_time
print(total_time)
