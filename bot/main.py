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

from tools import trade, strategy, models, loggs
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
        self.symbol = settings.SYMBOL
        self.signal_data = {}

    def _connect_db(self):
        try:
            from tools.models import Base
            Base.metadata.create_all(self.engine)
            session = self.SessionLocal()
            return session
        except Exception as e:
            loggs.error_logs_logger.error(f'Error while connecting to db: {e}')
            return None

    def _store_data(self):
        session = self._connect_db()
        if session:
            try:
                new_trade = models.Trade(
                    symbol=self.symbol,
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
            try:
                signal_data = strategy.check_crossover()
                if not signal_data:
                    loggs.system_log.info('No signal data received.')
                    time.sleep(3 * 60)
                    continue

                self.signal_data = {
                    "side": signal_data[0],
                    "entry_price": float(signal_data[1]),
                    "adx": float(signal_data[2]),
                    "atr": float(signal_data[3]),
                    "rsi": float(signal_data[4]),
                    "long_ema": float(signal_data[5]),
                    "short_ema": float(signal_data[6]),
                    "volume": float(signal_data[7])
                }

                if self.signal_data["side"] == 'long':
                    ON_TRADE = True
                    loggs.system_log.info(f"Getting long signal with entry price: {self.signal_data['entry_price']}")
                    _, pnl, target_price = trade.long_trade(
                        entry_price=self.signal_data['entry_price'],
                        atr=self.signal_data['atr']
                    )
                    self.signal_data['pnl'] = pnl
                    self.signal_data['exit_price'] = float(target_price)
                    self._store_data()

                elif self.signal_data['side'] == "short":
                    ON_TRADE = True

                    loggs.system_log.info(f"Getting short signal with entry price: {self.signal_data['entry_price']}")
                    _, pnl, target_price = trade.short_trade(
                        entry_price=self.signal_data['entry_price'],
                        atr=self.signal_data['atr']
                    )
                    self.signal_data['pnl'] = pnl
                    self.signal_data['exit_price'] = float(target_price)
                    self._store_data()

                else:
                    loggs.system_log.info('No trades at this moment')
            except Exception as e:
                loggs.error_logs_logger.error(f"Error while checking crossover: {e}")
            time.sleep(3 * 60)


def restart_check_signal():
    """Stops the existing check_signal thread, reloads settings, and starts a new one."""
    global check_signal_thread

    loggs.system_log.info("🛑 Stopping check_signal thread...")
    stop_event.set()  # Stop the previous thread

    # Give some time to fully stop the thread before restarting
    if check_signal_thread and check_signal_thread.is_alive():
        check_signal_thread.join(timeout=5)  # Avoid indefinite blocking

    # 🔄 Reload settings
    importlib.reload(settings)
    loggs.system_log.info("🔄 Reloaded settings module")
    # ✅ Start a new bot instance with updated settings
    bot = Bot()

    # ✅ Restart the check_signal thread
    stop_event.clear()
    check_signal_thread = threading.Thread(target=bot.check_signal, daemon=True)
    check_signal_thread.start()

    loggs.system_log.info("🚀 Restarted check_signal thread successfully!")
    signal_path = './tools/signal'
    if os.path.exists(signal_path):
        os.remove(signal_path)

def start_monitoring():
    """Starts monitoring the tools directory for changes."""

    event_handler = DirectoryChangeHandler(directory=MONITORING_DIR, restart_func=restart_check_signal)
    observer = Observer()
    observer.schedule(event_handler, path=MONITORING_DIR, recursive=True)  # Monitor files inside subdirectories too
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    loggs.system_log.info("Starting bot...")

    restart_check_signal()  # Start check_signal initially
    start_monitoring()