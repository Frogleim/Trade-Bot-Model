from binance.client import Client
import datetime

# Initialize the Binance Client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Fetch the latest trades for a symbol (e.g., BTCUSDT futures)
symbol = 'BTCUSDT'
trades = client.futures_recent_trades(symbol=symbol)

# Display trades with readable time
for trade in trades:

    # Convert the trade time from milliseconds to seconds
    timestamp_in_seconds = trade['time'] / 1000
    # Convert to a readable datetime
    readable_time = datetime.datetime.fromtimestamp(timestamp_in_seconds)
    # Add readable time to the trade data
    trade['readable_time'] = readable_time.strftime('%Y-%m-%d %H:%M:%S')

    # Print the trade including the readable time
    print(f"Trade ID: {trade['id']}, Price: {trade['price']}, Quantity: {trade['qty']}, Time: {trade['readable_time']}")
