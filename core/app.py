from core.util.socket_binance import get_last_price
from binance.client import Client
import time
import loggs
import ta
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')
loggs.system_log.info('Loading .env file')
client = Client()
symbol = "BTCUSDT"
interval = '15m'




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


