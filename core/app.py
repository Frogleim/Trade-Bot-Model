from socket_binance import fetch_btcusdt_klines, get_last_price
from binance.client import Client
import time
import loggs
import ta
from dotenv import load_dotenv
import os
from position_handler import place_buy_order, place_sell_order, close_position

load_dotenv(dotenv_path='.env')
loggs.system_log.info('Loading .env file')
client = Client()
symbol = os.environ.get('SYMBOL')
interval = os.environ.get('INTERVAL')


def calculate_support_resistance(df):
    """Calculate support and resistance levels."""
    recent_lows = df['low'].rolling(window=20).min()
    recent_highs = df['high'].rolling(window=20).max()
    support = recent_lows.iloc[-1]  # Current support level
    resistance = recent_highs.iloc[-1]  # Current resistance level
    return support, resistance


def calculate_ema_and_sr():
    """Calculate EMA and Support/Resistance."""
    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print("No data fetched.")
        return None, None, None, None, None, None
    short_ema = df['close'].ewm(span=int(os.environ.get('SHORT_EMA')), adjust=False).mean().iloc[-1]
    long_ema = df['close'].ewm(span=int(os.environ.get('LONG_EMA')), adjust=False).mean().iloc[-1]
    close_price_series = df['close']
    atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=int(os.environ.get('ATR_PERIOD'))).iloc[-1]
    support, resistance = calculate_support_resistance(df)
    current_price = close_price_series.iloc[-1]
    return current_price, atr, support, resistance, short_ema, long_ema


def check_signals_with_ema():
    """Check for entry and exit signals based on EMA + Support and Resistance."""
    current_price, atr, support, resistance, short_ema, long_ema = calculate_ema_and_sr()

    # Long Entry: Price hits support and uptrend (short EMA > long EMA)
    if current_price <= support and short_ema > long_ema:
        loggs.system_log.info(f'Price hit support: {support}. Uptrend confirmed. Long entry signal.')
        return ['Long', current_price, support, resistance]

    # Short Entry: Price hits resistance and downtrend (short EMA < long EMA)
    elif current_price >= resistance and short_ema < long_ema:
        loggs.system_log.info(f'Price hit resistance: {resistance}. Downtrend confirmed. Short entry signal.')
        return ['Short', current_price, support, resistance]

    else:
        return ['Hold', current_price, support, resistance]

def long_trade(entry_price, target_resistance):
    """Monitoring long trade with exit at next resistance."""
    loggs.system_log.warning(f'Buy position placed successfully: Entry Price: {entry_price}')
    # place_buy_order(quantity=0.002, symbol=symbol)

    stop_loss = entry_price - (target_resistance - entry_price) * 0.5

    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            loggs.system_log.error(f"Error fetching price: {e}")
            time.sleep(1)
            continue

        loggs.system_log.info(f'Long trade - Entry: {entry_price}, Target: {target_resistance}, '
                              f'Current: {current_price}, Stop Loss: {stop_loss}')
        if current_price >= target_resistance:
            # close_position(symbol=symbol)
            loggs.system_log.info(f'Target hit! Profit at {target_resistance}')
            return 'Profit'
        elif current_price <= stop_loss:
            # close_position(symbol=symbol)
            loggs.system_log.warning(f'Stop loss hit. Loss at {stop_loss}')
            return 'Loss'
        time.sleep(1)


def short_trade(entry_price, target_support):
    """Monitoring short trade with exit at next support."""
    loggs.system_log.warning(f'Sell position placed successfully: Entry Price: {entry_price}')
    # place_sell_order(quantity=0.002, symbol=symbol)

    stop_loss = entry_price + (entry_price - target_support) * 0.5

    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            loggs.system_log.error(f"Error fetching price: {e}")
            time.sleep(1)
            continue

        loggs.system_log.info(f'Short trade - Entry: {entry_price}, Target: {target_support}, '
                              f'Current: {current_price}, Stop Loss: {stop_loss}')
        if current_price <= target_support:
            # close_position(symbol=symbol)
            loggs.system_log.info(f'Target hit! Profit at {target_support}')
            return 'Profit'
        elif current_price >= stop_loss:
            # close_position(symbol=symbol)
            loggs.system_log.warning(f'Stop loss hit. Loss at {stop_loss}')
            return 'Loss'
        time.sleep(1)


if __name__ == '__main__':
    while True:
        signal = check_signals()
        if signal[0] == 'long':
            long_trade(entry_price=signal[1], target_resistance=signal[3])
        elif signal[0] == 'short':
            short_trade(entry_price=signal[1], target_support=signal[2])
        else:
            loggs.system_log.info(f'No entry signal. Holding position.')
        time.sleep(60)  # Wait 1 minute before checking for a new signal
