from binance.client import Client
import pandas as pd
import joblib
import talib
from sklearn.model_selection import train_test_split
import time
from datetime import datetime, timedelta

api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

def fetch_live_data(symbol, interval='15m'):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=200)  # Limit to get the last 200 candles
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

symbol = 'BTCUSDT'
live_data = fetch_live_data(symbol)

def preprocess_live_data(data):
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['EMA_14'] = data['close'].ewm(span=14, adjust=False).mean()
    data['RSI'] = talib.RSI(data['close'], timeperiod=14)

    # Ensure no NaN values before prediction
    data = data.dropna()
    return data


processed_data = preprocess_live_data(live_data)
X = processed_data[['SMA_50', 'EMA_14', 'RSI']]
y = processed_data['close']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
loaded_model = joblib.load('./model/linear_regression_model.pkl')
y_pred_live = loaded_model.predict(X_test)  # or use it for live data
print(f'Predicted values: {y_pred_live}')

def get_prediction():
    live_data = fetch_live_data(symbol)
    processed_data = preprocess_live_data(live_data)
    latest_data = processed_data[['SMA_50', 'EMA_14', 'RSI']].iloc[-1].values.reshape(1, -1)
    predicted_price = loaded_model.predict(latest_data)
    next_prediction_time = datetime.now() + timedelta(minutes=15)
    next_prediction_time_str = next_prediction_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Predicted next close price at {next_prediction_time_str}: {predicted_price[0]}")
    return predicted_price[0]