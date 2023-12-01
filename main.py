import time
from core import profitable_exit_strategy, config


def start():
    while True:
        profitable_exit_strategy.trade()
        time.sleep(config.TRADE_INTERVAL)


if __name__ == '__main__':
    start()
