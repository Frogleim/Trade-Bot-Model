import pandas as pd

def predict_trade_success_xgb(trade_signal):
    # Convert dictionary into DataFrame
    import xgboost as xgb


# Load the saved XGBoost model
    model = xgb.XGBClassifier()
    model.load_model("xgboost_model.model")
    trade_df = pd.DataFrame([trade_signal])

    # Convert 'side' to numerical format
    trade_df["side"] = trade_df["side"].apply(lambda x: 1 if str(x).lower() == "long" else 0)  # ✅ Corrected
    # Normalize trade data
    trade_df[features] = scaler.transform(trade_df[features])

    # Predict probability of profitable trade
    probability = model.predict_proba(trade_df[features])[0][1]  # Class 1 probability

    # **🔥 New Trend Filtering:**
    is_trending = trade_signal["adx"] > 20

    # **🔥 New ATR Filtering: Avoid volatile trades**


    # Final Decision: Only open trade if all filters pass
    if probability > 0.85 and is_trending:
        trade_decision = "✅ OPEN TRADE"
    else:
        trade_decision = "❌ SKIP TRADE"

    return {
        "symbol": trade_signal["symbol"],
        "entry_price": trade_signal["entry_price"],
        "probability": round(probability * 100, 2),
        "trade_decision": trade_decision
    }