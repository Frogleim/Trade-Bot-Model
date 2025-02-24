import pandas as pd
import xgboost as xgb
from .socket_binance import fetch_btcusdt_klines
from binance.client import Client
from . import loggs
from .settings import settings
import ta
from dotenv import load_dotenv
from .ai_model import predict_signal
import os
import importlib
import pickle

current_dir = os.getcwd()

# Load the trained AI model
xgb_model = xgb.XGBClassifier()
model_path = os.path.join(current_dir, "tools/model/xgboost_model.model")
scaler_path = os.path.join(current_dir, "tools/model/scaler.pkl")
xgb_model.load_model(model_path)
load_dotenv(dotenv_path='./tools/.env')

client = Client()
symbols = settings.SYMBOLS  # Update settings to include a list of symbols
interval = settings.INTERVAL
adx_period = settings.ADX_PERIOD

features = ['entry_price', 'long_ema', 'short_ema', 'adx', 'atr', 'rsi', 'volume', 'side']

with open(scaler_path, "rb") as file:
    scaler = pickle.load(file)


def normalize_trade_data(trade_df):
    trade_df["side"] = trade_df["side"].apply(lambda x: 1 if str(x).lower() == "long" else 0)  # Convert side
    trade_df[features] = scaler.transform(trade_df[features])  # Normalize features
    return trade_df


def calculate_ema(symbol):
    """Calculating indicators for fast execution scalping strategy for a given symbol"""
    importlib.reload(settings)

    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print(f"No data fetched for {symbol}.")
        return None, None, None, None, None, None, None

    # Calculate EMAs
    short_ema = df['close'].ewm(span=int(settings.SHORT_EMA), adjust=False).mean()
    long_ema = df['close'].ewm(span=int(settings.LONG_EMA), adjust=False).mean()

    # Calculate RSI
    df['previous_close'] = df['close'].shift(1)
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Calculate ATR
    atr_period = int(os.getenv('ATR_PERIOD'))
    df['high_low'] = df['high'] - df['low']
    df['high_prev_close'] = abs(df['high'] - df['previous_close'])
    df['low_prev_close'] = abs(df['low'] - df['previous_close'])
    df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
    df['ATR'] = df['true_range'].rolling(window=atr_period).mean()
    atr = df['ATR'].iloc[-1]

    # Calculate ADX
    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)

    # Volume Data
    volume = df['volume']

    loggs.system_log.info(
        f'{symbol} - Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {atr} ADX: {adx.iloc[-1]} '
        f'RSI: {rsi.iloc[-1]} Volume: {volume.iloc[-1]}')

    return long_ema, short_ema, df['close'], adx, atr, rsi, volume


def identify_levels(df, window=20):
    """Identify local support and resistance levels using rolling min/max"""
    df['resistance'] = df['high'].rolling(window=window).max().shift(1)
    df['support'] = df['low'].rolling(window=window).min().shift(1)
    return df


def detect_breakout(symbol, volume_threshold=1.5):

    """Detect breakout when the price closes above resistance or below support with high volume"""
    df = fetch_btcusdt_klines(symbol, interval)

    df['resistance'] = df['high'].rolling(window=20).max().shift(1)
    df['support'] = df['low'].rolling(window=20).min().shift(1)
    df["prev_resistance"] = df["resistance"].shift(1)
    df["prev_support"] = df["support"].shift(1)
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")  # Convert to float, coerce errors to NaN

    df["breakout_up"] = (df["close"] > df["prev_resistance"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)
    df["breakout_down"] = (df["close"] < df["prev_support"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)

    return df



# AI-based trade validation function
def predict_trade_success_xgb(trade_signal):
    trade_df = pd.DataFrame([trade_signal])
    trade_df = normalize_trade_data(trade_df)  # Normalize features

    # Predict probability of profitable trade
    probability = xgb_model.predict_proba(trade_df[features])[0][1]  # Class 1 probability

    # Apply AI filters
    is_trending = trade_signal["adx"] > 20
    loggs.system_log.info(f'Profit probability: {probability} is trending: {is_trending}')
    if probability > 0.85 and is_trending:
        return True  # ✅ AI approves trade
    return False  # ❌ AI rejects trade

# Modify `check_crossover()` to integrate AI decision
def check_crossover(symbol):
    long_ema, short_ema, close_price_series, adx, atr, rsi, volume = calculate_ema(symbol)

    def safe_convert(series):
        return pd.to_numeric(series, errors='coerce') if series is not None else None

    long_ema = safe_convert(long_ema)
    short_ema = safe_convert(short_ema)
    close_price_series = safe_convert(close_price_series)
    adx = safe_convert(adx)
    atr = float(atr) if atr is not None else None
    rsi = safe_convert(rsi)
    volume = safe_convert(volume)

    if any(data is None or isinstance(data, pd.Series) and data.isnull().all() for data in
           [short_ema, long_ema, close_price_series, adx, atr, rsi, volume]):
        loggs.system_log.error(f"{symbol} - Missing or invalid data. Skipping crossover check.")
        return [symbol, 'Hold', None, None, None, None, None, None, None]

    prev_short, prev_long = short_ema.iloc[-2], long_ema.iloc[-2]
    curr_short, curr_long = short_ema.iloc[-1], long_ema.iloc[-1]
    prev_price, curr_price = close_price_series.iloc[-2], close_price_series.iloc[-1]

    if any(pd.isna(val) for val in [prev_short, prev_long, curr_short, curr_long, prev_price, curr_price]):
        loggs.system_log.error(f"{symbol} - NaN values detected. Skipping crossover check.")
        return [symbol, 'Hold', None, None, None, None, None, None, None]

    crossover_buy = curr_short > curr_long and prev_short < prev_long
    strong_trend = adx.iloc[-1] > 25

    crossover_sell = curr_short < curr_long and prev_short > prev_long
    strong_trend_sell = adx.iloc[-1] > 25

    is_breakout = detect_breakout(symbol)

    # 🔥 AI-Enhanced Decision

    if (crossover_buy or is_breakout['breakout_up'].iloc[-1]) and strong_trend:
        trade_signal = {
            "symbol": symbol,
            "entry_price": curr_price,
            "long_ema": curr_long,
            "short_ema": curr_short,
            "adx": adx.iloc[-1],
            "atr": atr,
            "rsi": rsi.iloc[-1],
            "volume": volume.iloc[-1],
            "side": "long"
        }
        loggs.debug_log.debug(trade_signal)
        ai_approved = predict_signal(trade_signal)
        loggs.debug_log.debug(ai_approved)
        if ai_approved['trade_decision']:
            loggs.system_log.info(f"{symbol} - XGBoost approved. Probability: {ai_approved['probability']}")
            return [symbol, 'long', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    elif (crossover_sell or is_breakout['breakout_down'].iloc[-1]) and strong_trend_sell:
        trade_signal = {
            "symbol": symbol,
            "entry_price": curr_price,
            "long_ema": curr_long,
            "short_ema": curr_short,
            "adx": adx.iloc[-1],
            "atr": atr,
            "rsi": rsi.iloc[-1],
            "volume": volume.iloc[-1],
            "side": "short"
        }
        loggs.debug_log.debug(trade_signal)
        ai_approved = predict_signal(trade_signal)
        loggs.debug_log.debug(ai_approved)
        if ai_approved['trade_decision']:
            loggs.system_log.info(f"{symbol} - XGBoost approved. Probability: {ai_approved['probability']}")
            return [symbol, 'short', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    else:
        return [symbol, 'Hold', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]


def monitor_cryptos():
    """Monitor signals for multiple cryptocurrencies"""
    results = []
    for symbol in symbols:
        result = check_crossover(symbol)
        results.append(result)

    df_results = pd.DataFrame(results,
                              columns=['Symbol', 'Signal', 'Price', 'ADX', 'ATR', 'RSI', 'Long EMA', 'Short EMA',
                                       'Volume'])
    return df_results


if __name__ == '__main__':
    signal = {'symbol': 'BNBUSDT', 'entry_price': 634.51, 'long_ema': 645.8372928628042, 'short_ema': 641.0374842057347,
     'adx': 55.71942338106728, 'atr': 3.4835714285714436, 'rsi': 16.25754527162968, 'volume': 20343.69, 'side': 'short'}
    predict_trade_success_xgb(signal)