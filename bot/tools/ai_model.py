import xgboost as xgb

import pandas as pd

import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

current_dir = os.getcwd()
features = ['entry_price', 'long_ema', 'short_ema', 'adx', 'atr', 'rsi', 'volume', 'side']
model_path = os.path.join(current_dir, "tools/model/xgboost_model.model")
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


if __name__ == "__main__":
    signal = {'symbol': 'BNBUSDT', 'entry_price': 637.68, 'long_ema': 648.1396607276297, 'short_ema': 644.4841940714603, 'adx': 50.47003009354349, 'atr': 3.5028571428571564, 'rsi': 28.611898016997003, 'volume': 24773.65, 'side': 'short'}
    res = predict_trade_success_xgb(signal)
    print(res)