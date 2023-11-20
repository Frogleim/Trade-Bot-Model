import time
from core import make_trades


def start_reverse():
    while True:
        make_trades.reverse_trade()
        time.sleep(10)


if __name__ == '__main__':
    start_reverse()
    # 80
    #
