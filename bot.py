from coins_trade.miya import miya_trade
from colorama import init, Fore
from binance.client import Client
from db import DataBase
from coins_trade.miya import logging_settings

import time

client = Client()


def start_trade():
    my_db = DataBase()
    signal_data = my_db.get_signal()
    if signal_data is not None:
        row = my_db.get_trade_coins(signal_data[4])
        signal = signal_data[2]
        entry_price = signal_data[3]
        miya_trade.trade(
            symbol=row[1],
            signal=signal,
            entry_price=entry_price,
            position_size=row[2],
            indicator=row[-1]
        )
        my_db.clean_db(table_name='signals')
        logging_settings.system_log.warning('Signals Table cleaned successfully')
        traded = True
        return traded
    else:
        print('No trading signal')


if __name__ == '__main__':
    print(Fore.YELLOW + 'Starting trade bot...')
    while True:
        is_traded = start_trade()
        time.sleep(5)
