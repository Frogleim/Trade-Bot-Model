import time
from core import make_trades


def start():
    while True:
        make_trades.trade()
        time.sleep(5)


if __name__ == '__main__':
    start()
