from logging.config import ConvertingList
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os


DATABASE_URL = 'postgresql://postgres:admin@localhost:5433/tb'
loaded = load_dotenv(dotenv_path=os.path.abspath('./tools/.env'))
print(f"Dotenv loaded: {loaded}")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Trade(Base):

    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)
    long_ema = Column(Float, nullable=False)
    short_ema = Column(Float, nullable=False)
    adx = Column(Float, nullable=False)
    atr = Column(Float, nullable=False)
    rsi = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    side = Column(String, nullable=False)



