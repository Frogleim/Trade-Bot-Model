import time
from binance.client import Client
from . import position_handler, logging_settings, api_connect, monitor_position
from binance.exceptions import BinanceAPIException


miya_api = api_connect.API()
keys_data = miya_api.get_binance_keys()
API_KEY = keys_data['api_key']
API_SECRET = keys_data['api_secret']
client = Client(API_KEY, API_SECRET)


def trade(symbol, signal, entry_price, position_size, indicator):
    print(signal)
    miya_api.clean_db(table_name='signals')
    logging_settings.system_log.warning(f'Starting trade. Symbol: {symbol}, '
                                        f'Entry Price: {entry_price}, Position Size: {position_size}')
    if signal == 'Sell':
        start_time = time.time()
        print(f'Trade starting time: {start_time}')


        try:
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=position_size,
                                                           symbol=symbol)
        except Exception as e:
            logging_settings.error_logs_logger.error(e)
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=position_size,
                                                           symbol=symbol)
        while True:

            try:
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            except BinanceAPIException as be:
                logging_settings.error_logs_logger.error(be)
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))

            if open_orders['status'] == 'NEW':
                total_time = time.time() - start_time
                print(f'Total waiting time: {total_time}')
                if time.time() - start_time > 60:
                    client.futures_cancel_order(symbol=symbol, orderId=int(order_info['orderId']))
                    logging_settings.system_log.warning('Trade wasn\'t finished...too much time passed')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')

                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')
                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                miya_api.insert_is_finished()
                miya_api.clean_db(table_name='signals')

                break
            if open_orders['status'] == 'FILLED':
                res = monitor_position.monitor_position_short(entry_price)
                if res == 'Profit':

                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(symbol=symbol)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(symbol=symbol)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')

                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')

                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(symbol=symbol)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(symbol=symbol)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')

                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')

                    break

    if signal == 'Buy':
        start_time = time.time()
        print(f'Trade starting time: {start_time}')


        try:
            order_info = position_handler.place_buy_order(price=entry_price, quantity=position_size,
                                                          symbol=symbol)
        except Exception as e:
            logging_settings.error_logs_logger.error(e)
            order_info = position_handler.place_buy_order(price=entry_price, quantity=position_size,
                                                          symbol=symbol)
        while True:

            try:
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            except BinanceAPIException as be:
                logging_settings.error_logs_logger.error(be)
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))

            if open_orders['status'] == 'NEW':
                total_time = time.time() - start_time

                print(f'Total waiting time: {total_time}')

                if time.time() - start_time > 60:
                    client.futures_cancel_order(symbol=symbol, orderId=int(order_info['orderId']))
                    logging_settings.system_log.warning('Trade wasn\'t finished...too much time passed')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')

                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                miya_api.insert_is_finished()
                miya_api.clean_db(table_name='signals')

                break
            if open_orders['status'] == 'FILLED':
                res = monitor_position.monitor_position_long(entry_price)
                if res == 'Profit':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(symbol=symbol)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(symbol=symbol)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')

                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(symbol=symbol)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(symbol=symbol)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    miya_api.insert_is_finished()
                    miya_api.clean_db(table_name='signals')

                    break


if __name__ == '__main__':
    trade(symbol='BTCUSDT', signal='Sell', entry_price=50000, position_size=0.002, indicator='EMA')