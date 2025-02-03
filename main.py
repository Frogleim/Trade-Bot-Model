import time
from tools import trade, strategy, models, loggs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r'./tools/.env')


class Bot:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY', '')
        self.api_secret = os.getenv('BINANCE_API_SECRET', '')
        self.db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.db_url)
        self.Base = declarative_base()
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.symbol = os.getenv("SYMBOL")
        self.signal_data = {}

    def _connect_db(self):
        try:
            self.Base.metadata.create_all(self.engine)
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
                    entry_price=self.signal_data['entry_price'],
                    exit_price=self.signal_data['exit_price'],
                    pnl=self.signal_data['pnl'],
                    long_ema=self.signal_data['long_ema'],
                    short_ema=self.signal_data['short_ema'],
                    adx=self.signal_data['adx'],
                    atr=self.signal_data['atr'],
                    rsi=self.signal_data['rsi'],
                    volume=self.signal_data['volume'],
                    side=self.signal_data['side']
                )
                session.add(new_trade)
                session.commit()
            except Exception as e:
                loggs.error_logs_logger.error(f'Error while storing data: {e}')
                session.rollback()
            finally:
                session.close()

    def check_signal(self):
        while True:
            try:
                signal_data = strategy.check_crossover()
                print(signal_data)
                self.signal_data = {
                    "side": signal_data[0],
                    "entry_price": signal_data[1],
                    "adx": signal_data[2],
                    "atr": signal_data[3],
                    "rsi": signal_data[4],
                    "long_ema": signal_data[5],
                    "short_ema": signal_data[6],
                    "volume": signal_data[7]
                }
                print(self.signal_data)

                if self.signal_data["side"] == 'long':
                    loggs.system_log.info(f"Getting long signal with entry price: {self.signal_data['entry_price']}")
                    pnl, atr, target_price = trade.long_trade(
                        entry_price=self.signal_data['entry_price'],
                        atr=self.signal_data['atr']
                    )
                    self.signal_data['pnl'] = pnl
                    self.signal_data['exit_price'] = target_price
                    self._store_data()

                elif self.signal_data['side'] == "short":
                    loggs.system_log.info(f"Getting short signal with entry price: {self.signal_data['entry_price']}")
                    pnl, atr, target_price = trade.short_trade(
                        entry_price=self.signal_data['entry_price'],
                        atr=self.signal_data['atr']
                    )
                    self.signal_data['pnl'] = pnl
                    self.signal_data['exit_price'] = target_price
                    self._store_data()

                else:
                    loggs.system_log.info('No trades at this moment')
            except Exception as e:
                loggs.error_logs_logger.error(f"Error while checking crossover: {e}")
            time.sleep(3*60)
if __name__ == '__main__':
    myBot = Bot()
    myBot.check_signal()