from binance.client import Client
import ta
import time
import requests
from scipy.special import additional

from socket_binance import fetch_btcusdt_klines


def write_system_state(e):
    with open("system_state.txt", 'w') as file:
        file.write(f'Not working\nReason {e}')


def get_credentials():
    print('Getting API KEYS from db')
    url = "http://77.37.51.134:8080/get_keys"
    headers = {
        "accept": "application / json"
    }
    response = requests.get(url=url, headers=headers, verify=False)
    return response.json()


client = Client()
symbol = 'BTCUSDT'
interval = '15m'
lookback = 5
adx_period = 14


def calculate_ema():
    """Calculating indicators"""
    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print("No data fetched.")
        return None, None, None, None, None
    short_ema = df['close'].ewm(span=5, adjust=False).mean()
    long_ema = df['close'].ewm(span=13, adjust=False).mean()
    close_price = df['close'].iloc[-2]
    df['previous_close'] = df['close'].shift(1)
    df['high_low'] = df['high'] - df['low']
    df['high_prev_close'] = abs(df['high'] - df['previous_close'])
    df['low_prev_close'] = abs(df['low'] - df['previous_close'])
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_sma = rsi.rolling(window=14).mean()
    df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
    atr_period = 14
    df['ATR'] = df['true_range'].rolling(window=atr_period).mean()

    # Fetch the latest ATR value
    atr = df['ATR'].iloc[-1]
    adx_period = 14
    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
    print(
        f'Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {df["ATR"].iloc[-2]} ADX: {adx.iloc[-1]}'
        f' RSI: {rsi.iloc[-1]} RSI SMA: {rsi_sma.iloc[-1]}')
    return long_ema, short_ema, close_price, adx, atr, rsi


def check_crossover():
    """Check for signal with based strategy"""
    long_ema, short_ema, close_price, adx, atr, rsi = calculate_ema()
    missing_data = {}
    if short_ema is None or len(short_ema) < 2:
        missing_data['short_ema'] = 'Missing or invalid'
    if long_ema is None or len(long_ema) < 2:
        missing_data['long_ema'] = 'Missing or invalid'
    if close_price is None:
        missing_data['close_price'] = 'Missing'
    if adx is None or len(adx) == 0 or adx.iloc[-1] is None:
        missing_data['adx'] = 'Missing or invalid'
    if atr is None or float(atr) <= 0:
        missing_data['atr'] = 'Missing or invalid'
    if missing_data:
        raise ValueError(f"Missing or invalid crossover data: {missing_data}")
    crossover_sell = (short_ema.iloc[-2] < long_ema.iloc[-2]) and (short_ema.iloc[-1] > long_ema.iloc[-1])
    crossover_buy = (short_ema.iloc[-2] > long_ema.iloc[-2]) and (short_ema.iloc[-1] < long_ema.iloc[-1])
    additional_indicator_long = (adx.iloc[-1] > 20) and (rsi.iloc[-1] > 50) and (atr > 120)
    additional_indicator_short = (adx.iloc[-1] > 20) and (rsi.iloc[-1] < 50) and (atr > 120)

    print(f"ADX: {adx.iloc[-1]}, ATR: {atr}, Crossover Buy: {crossover_buy}, Crossover Sell: {crossover_sell}")
    if crossover_buy and additional_indicator_long:
        return ['long', close_price, adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1], short_ema.iloc[-1]]
    elif crossover_sell and additional_indicator_short:
        return ['short', close_price, adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1], short_ema.iloc[-1]]
    else:
        return ['Hold', close_price, adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1], short_ema.iloc[-1]]



def long_trade(entry_price, atr):
    """Monitoring long trade"""
    target_price = entry_price + atr
    stop_loss = entry_price - atr

    while True:
        try:
            current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        print(f'Target price: {target_price}, Current price: {current_price} Stop loss: {stop_loss}')
        if current_price >= target_price:
            return 'Profit', atr, target_price
        elif current_price <= stop_loss:
            return 'Loss', -atr, stop_loss
        time.sleep(1)

def short_trade(entry_price, atr):
    """Monitoring short trade"""
    target_price = entry_price - atr
    stop_loss = entry_price + atr
    while True:
        try:
            current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        print(f'Target price: {target_price}, Current price: {current_price}')
        if current_price <= target_price:
            return 'Profit', atr, target_price
        elif current_price > stop_loss:
            return 'Loss', -atr, stop_loss
        time.sleep(1)

# def start_trade(signal=None, close_price=None):
#
#     signal, close_price = check_crossover()
#     client.futures_change_leverage(leverage=125, symbol='BTCUSDT')
#     try:
#         if signal == 'Buy':
#             logging_settings.system_log.warning(f'Buy position placed successfully: Entry Price: {close_price}')
#             miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
#             logging_settings.system_log.warning('Trade finished! Sleeping...')
#             time.sleep(900)
#         elif signal == 'Sell':
#             logging_settings.system_log.warning(f'Sell position placed successfully. Entry Price: {close_price}')
#             miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
#             logging_settings.system_log.warning('Trade finished! Sleeping...')
#             time.sleep(900)
#         else:
#             print('Hold, not crossover yet')
#     except Exception as error:
#         logging_settings.error_logs_logger.error(error)


if __name__ == '__main__':
    while True:
        crossover_result = check_crossover()
        print(crossover_result[0])
