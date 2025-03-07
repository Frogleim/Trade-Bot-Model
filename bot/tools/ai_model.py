import xgboost as xgb
import pandas as pd
from joblib import load
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timezone
import os
import time
from binance.client import Client
from . import loggs


client = Client()

current_dir = os.getcwd()
features = ['entry_price', 'long_ema', 'short_ema', 'adx', 'atr', 'rsi', 'volume', 'side']
model_path = os.path.join(current_dir, "tools/model/xgboost_model.model")
next_price_model = os.path.join(current_dir, "tools/model/model.joblib")
trade_data_path = os.path.join(current_dir, "tools/trade_data/trades_data_xboost.csv")

def read_trade_data():
    df = pd.read_csv(trade_data_path)
    return df

def scal_data():
    df = read_trade_data()

    df["side"] = df["side"].astype(str).str.lower()

    # Convert 'side' to numerical format if it's an object
    if df["side"].dtype == 'object':
        df["side"] = df["side"].apply(lambda x: 1 if x.lower() == "long" else 0)

    # Define feature columns and target
    target = 'Label'  # 1 for profitable trades, 0 for unprofitable trades

    # Initialize and fit scaler
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])

    # Save the trained scaler
    # with open("scaler.pkl", "wb") as file:
    #     pickle.dump(scaler, file)
    #
    # print("✅ Scaler saved successfully!")
    return scaler


def predict_signal(trade_signal):
    # Convert dictionary into DataFrame
    import xgboost as xgb

    scaler = scal_data()

# Load the saved XGBoost model
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    trade_df = pd.DataFrame([trade_signal])

    # Convert 'side' to numerical format
    trade_df["side"] = trade_df["side"].apply(lambda x: 1 if str(x).lower() == "long" else 0)  # ✅ Corrected
    # Normalize trade data
    trade_df[features] = scaler.transform(trade_df[features])

    # Predict probability of profitable trade
    probability = model.predict_proba(trade_df[features])[0][1]  # Class 1 probability

    # **🔥 New Trend Filtering:**
    is_trending = trade_signal["adx"] > 20

    # Final Decision: Only open trade if all filters pass
    if probability > 0.85 and is_trending:
        trade_decision = True
    else:
        trade_decision = False

    return {
        "symbol": trade_signal["symbol"],
        "entry_price": trade_signal["entry_price"],
        "probability": round(probability * 100, 2),
        "trade_decision": trade_decision
    }


def next_price_prediction(symbols):


    model = load(next_price_model)

    # while True:
    current_time = pd.Timestamp(datetime.now(timezone.utc))
    klines = client.futures_klines(symbol=symbols, interval=Client.KLINE_INTERVAL_1HOUR, limit=30)
    df_live = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
'close_time', 'quote_asset_volume', 'number_of_trades',
'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df_live['close_time'] = pd.to_datetime(df_live['close_time'], unit='ms', utc=True)

    df_live = df_live[df_live['close_time'] <= current_time].tail(25)
    closes = df_live['close'].astype(float).values
    print(closes[-1])
    feature_dict = {'close': closes[23]}
    for i in range(1, 25):
        feature_dict[f'close_t-{i}'] = closes[24 - i]
    X_live = pd.DataFrame([feature_dict])
    prediction = model.predict(X_live)[0]
    loggs.system_log.info(f"{current_time}: Predicted next hour close: {prediction}")
    if prediction > closes[-1]:
        return True
    elif prediction < closes[-1]:
        return False
    # time.sleep(3600)


if __name__ == "__main__":
    is_signal = next_price_prediction()
    print(is_signal)