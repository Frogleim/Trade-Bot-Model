import warnings

warnings.filterwarnings(action='ignore')

import asyncio

from core.strategies import EMA_Cross
from db import DataBase
from coins_trade.miya import logging_settings

my_db = DataBase()

pause_event = asyncio.Event()

symbols = ['MATICUSDT', 'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']


async def check_signal(symbol):
    return await EMA_Cross.check_signal(symbol)


async def monitor_and_check_signals():
    while True:
        try:
            tasks = [check_signal(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks)
            for result in results:
                print(result[1])
                if result[1] != 'Hold':
                    my_db.insert_signal(
                        symbol=result[0],
                        signal=result[1],
                        entry_price=result[2],
                        indicator='EMA'
                    )
                    pause_event.clear()  # Break out of the loop if a result is found
            else:
                print('No trade signals')
            await asyncio.sleep(1)  # Check every second
            is_finished = my_db.check_is_finished()
            if is_finished:
                my_db.clean_db(table_name='signals')
                my_db.clean_db(table_name='trades_alert')
                pause_event.set()  # Resume signal monitoring
        except Exception as e:
            logging_settings.error_logs_logger.error(f'EMA Crossover script down!\nError message: {e}')
        await asyncio.sleep(1)  # To avoid a tight loop


if __name__ == '__main__':
    my_db.create_all_tables()
    asyncio.run(monitor_and_check_signals())
