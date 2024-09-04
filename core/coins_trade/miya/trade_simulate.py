from binance.client import Client
from . import tp_sl, config, logging_settings, db
import time
from datetime import datetime

client = Client(config.API_KEY, config.API_SECRET)


def trade(symbol, signal, entry_price, start_time=None):
    current_time = datetime.now()

    if signal == 'Sell':
        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00
        trade_start = time.time()
        print(f'Trade starting time: {trade_start}')
        print(f'tp_sl.profit_checkpoint_list: {tp_sl.profit_checkpoint_list} --- {tp_sl.current_profit}')
        while True:
            current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            total_time = time.time() - trade_start
            if total_time > 60:
                print('Breaking! Waiting time is expired')

                break
            if float(entry_price) - float(current_price) < - 0.00011:
                res = tp_sl.pnl_short(entry_price, current_time)
                if res == 'Profit' and res is not None:
                    print(f'Closing Position with {res}')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break

    if signal == 'Buy':

        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00
        trade_start = time.time()

        print(f'tp_sl.profit_checkpoint_list: {tp_sl.profit_checkpoint_list} --- {tp_sl.current_profit}')
        while True:
            current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            total_time = time.time() - trade_start
            if total_time > 60:
                print('Breaking! Waiting time is expired')
                break
            if float(current_price) - float(entry_price) > 0.00011:
                res = tp_sl.pnl_long(entry_price, current_time, symbol=symbol)
                print(res)
                if res == 'Profit' and res is not None:
                    print(f'Closing Position with {res}')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break

