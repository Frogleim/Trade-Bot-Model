import csv
from binance.client import Client
import pandas as pd
from datetime import datetime

# Initialize Binance Client
api_key = 'your_api_key'  # Optional
api_secret = 'your_api_secret'  # Optional

client = Client(api_key, api_secret)

# Set parameters
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_date = "1 Jan, 2015"
end_date = "1 Jan, 2024"  # Optional

# Fetch historical klines
klines = client.get_historical_klines(symbol, interval, start_date, end_date)

# Convert to DataFrame
columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
df = pd.DataFrame(klines, columns=columns)

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Save to CSV
csv_file = f'{symbol}_{interval}_{start_date}_{end_date}.csv'
df.to_csv(csv_file, index=False)

print(f"Data saved to {csv_file}")
