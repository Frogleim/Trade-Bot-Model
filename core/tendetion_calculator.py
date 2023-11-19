from binance.client import Client
import time
import config

client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET)

ticker = client.futures_ticker(symbol=config.trading_pair)
print(ticker)
rh = ticker['highPrice']
rl = ticker['lowPrice']

# 'highPrice': '1972.01', 'lowPrice': '1916.00',
