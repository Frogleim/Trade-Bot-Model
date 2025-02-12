import time
import os
import threading
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import importlib

from tools import trade, strategy, models, loggs, pnl_calculator
from tools.settings import settings

stop_event = threading.Event()
check_signal_thread = None  # Store check_signal thread

load_dotenv(dotenv_path=r'./tools/.env')

Base = declarative_base()

MONITORING_DIR = "./tools"
ON_TRADE=False

class DirectoryChangeHandler(FileSystemEventHandler):
    """Monitors the tools directory for file changes and restarts check_signal if needed."""

    def __init__(self, directory, restart_func):
        self.directory = directory
        self.restart_func = restart_func
        self.files_snapshot = self._get_files_snapshot()

    def _get_files_snapshot(self):
        """Get a dictionary of file hashes to detect changes."""
        file_hashes = {}
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        file_hashes[file_path] = hashlib.md5(f.read()).hexdigest()
                except Exception as e:
                    loggs.system_log.error(f"Error hashing file {file_path}: {e}")
        return file_hashes

    def on_any_event(self, event):
        """Detects if a new file is added, deleted, or modified in the tools folder."""
        time.sleep(1)  # Small delay to avoid multiple triggers

        new_snapshot = self._get_files_snapshot()

        if new_snapshot != self.files_snapshot and not ON_TRADE:
            loggs.system_log.info('Change detected in tools directory. Restarting check_signal...')
            self.files_snapshot = new_snapshot  # Update snapshot
            stop_event.set()  # Stop the current check_signal process
            time.sleep(2)  # Give some time for the thread to stop
            self.restart_func()  # Restart the check_signal method


class Bot:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY', '')
        self.api_secret = os.getenv('BINANCE_API_SECRET', '')
        self.db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.symbols = settings.SYMBOLS  # Updated to handle multiple symbols
        self.signal_data = {}
        self.wallet_data = {}

    def _connect_db(self):
        try:
            from tools.models import Base
            Base.metadata.create_all(self.engine)
            session = self.SessionLocal()
            return session
        except Exception as e:
            loggs.error_logs_logger.error(f'Error while connecting to db: {e}')
            return None

    def _store_trade_data(self, symbol):
        session = self._connect_db()
        if session:
            try:
                new_trade = models.Trade(
                    symbol=symbol,
                    entry_price=self.signal_data.get('entry_price'),
                    exit_price=self.signal_data.get('exit_price'),
                    pnl=self.signal_data.get('pnl'),
                    long_ema=self.signal_data.get('long_ema'),
                    short_ema=self.signal_data.get('short_ema'),
                    adx=self.signal_data.get('adx'),
                    atr=self.signal_data.get('atr'),
                    rsi=self.signal_data.get('rsi'),
                    volume=self.signal_data.get('volume'),
                    side=self.signal_data.get('side')
                )
                session.add(new_trade)
                session.commit()
            except Exception as e:
                loggs.error_logs_logger.error(f'Error while storing data: {e}')
                session.rollback()
            finally:
                session.close()

    def check_signal(self):
        global ON_TRADE
        stop_event.clear()  # Clear the stop signal when starting

        while not stop_event.is_set():
            for symbol in self.symbols:
                try:
                    signal_data = strategy.check_crossover(symbol)
                    if not signal_data:
                        loggs.system_log.info(f'{symbol} - No signal data received.')
                        continue

                    self.signal_data = {
                        "side": signal_data[1],
                        "entry_price": float(signal_data[2]),
                        "adx": float(signal_data[3]),
                        "atr": float(signal_data[4]),
                        "rsi": float(signal_data[5]),
                        "long_ema": float(signal_data[6]),
                        "short_ema": float(signal_data[7]),
                        "volume": float(signal_data[8])
                    }

                    if self.signal_data["side"] in ['long', 'short']:
                        ON_TRADE = True
                        loggs.system_log.info(f"{symbol} - Getting {self.signal_data['side']} signal with entry price: {self.signal_data['entry_price']}")
                        trade_func = trade.long_trade if self.signal_data['side'] == 'long' else trade.short_trade
                        _, pnl, target_price = trade_func(
                            entry_price=self.signal_data['entry_price'],
                            atr=self.signal_data['atr']
                        )
                        self.signal_data['pnl'] = pnl
                        self.signal_data['exit_price'] = float(target_price)
                        self._store_trade_data(symbol)

                except Exception as e:
                    loggs.error_logs_logger.error(f"{symbol} - Error while checking crossover: {e}")
                time.sleep(10)  # Delay before checking next symbol


def restart_check_signal():
    global check_signal_thread

    loggs.system_log.info("🛑 Stopping check_signal thread...")
    stop_event.set()

    if check_signal_thread and check_signal_thread.is_alive():
        check_signal_thread.join(timeout=5)

    importlib.reload(settings)
    loggs.system_log.info("🔄 Reloaded settings module")
    bot = Bot()

    stop_event.clear()
    check_signal_thread = threading.Thread(target=bot.check_signal, daemon=True)
    check_signal_thread.start()

    loggs.system_log.info("🚀 Restarted check_signal thread successfully!")

if __name__ == '__main__':
    loggs.system_log.info("Starting bot...")
    restart_check_signal()