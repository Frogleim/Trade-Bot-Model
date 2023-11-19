import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core import make_trades
from importlib import reload


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'File {event.src_path} has been modified. Reloading...')
        reload(make_trades)


def start():
    while True:
        make_trades.trade()
        time.sleep(10)


if __name__ == '__main__':
    start()
    # 80
    #
