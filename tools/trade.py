from . import loggs, settings
import os
from .socket_binance import fetch_btcusdt_klines, get_last_price
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path='./tools/.env')

def long_trade(entry_price, atr):
    """Monitoring long trade"""
    loggs.system_log.warning(f'Buy position placed successfully: Entry Price: {entry_price}')

    if atr >= float(settings.ATR):
        target_price = entry_price + atr
        stop_loss = entry_price - (atr / 2)
    else:
        target_price = entry_price + float(settings.ATR)
        stop_loss = entry_price - (atr / 2 )
    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            loggs.error_logs_logger.error(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        loggs.system_log.info(f'Entry Price: {entry_price} Target price: {target_price}, '
                              f'Current price: {current_price} Stop loss: {stop_loss}')
        if current_price >= target_price:
            loggs.system_log.info('Trade finished successfully with profit')
            return 'Profit', atr, target_price
        elif current_price <= stop_loss:
            loggs.system_log.info('Trade finished successfully with loss')
            return 'Loss', -atr, stop_loss
        time.sleep(1)


def short_trade(entry_price, atr):
    """Monitoring short trade"""

    loggs.system_log.warning(f'Sell position placed successfully: Entry Price: {entry_price}')
    if atr >= settings.ATR:
        target_price = entry_price - settings.ATR
        stop_loss = entry_price + (atr / 2)
    else:
        target_price = entry_price - settings.ATR
        stop_loss = entry_price + (atr / 2)
    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            loggs.error_logs_logger.error(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        loggs.system_log.info(f'Entry Price: {entry_price} Target price: {target_price}, '
                              f'Current price: {current_price} Stop loss: {stop_loss}')
        if current_price <= target_price:
            loggs.system_log.info('Trade finished successfully with profit')
            return 'Profit', atr, target_price
        elif current_price > stop_loss:
            loggs.system_log.info('Trade finished successfully with loss')

            return 'Loss', -atr, stop_loss
        time.sleep(1)
