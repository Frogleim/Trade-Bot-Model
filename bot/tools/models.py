from sqlalchemy import create_engine, Column, Integer, String, Float, text, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

from dotenv import load_dotenv
import os

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

loaded = load_dotenv(dotenv_path=os.path.abspath('./tools/.env'))
print(f"Dotenv loaded: {loaded}")

DB_USER = "postgres"
DB_PASS = "admin"
DB_HOST = "pgdb"
DB_PORT = "5432"
DB_NAME = "tb"

default_engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres")

with default_engine.connect() as connection:
    connection.execution_options(isolation_level="AUTOCOMMIT")  # Disable transaction block
    result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"))

    if not result.scalar():
        connection.execute(text(f"CREATE DATABASE {DB_NAME}"))
        print(f"Database '{DB_NAME}' created successfully.")
    else:
        print(f"Database '{DB_NAME}' already exists.")

# Define the new engine for the `tb` database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Define the base model
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
    start_time = Column(DateTime, default=datetime.utcnow, nullable=True)  # When trade starts
    end_time = Column(DateTime, nullable=True)  # When trade ends, can be null


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    initial_balance = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    final_balance = Column(Float, nullable=False)


class Signal(Base):
    __tablename__ = 'signals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=True)
    entry_price = Column(Float, nullable=False)
    long_ema = Column(Float, nullable=False)
    short_ema = Column(Float, nullable=False)
    adx = Column(Float, nullable=False)
    atr = Column(Float, nullable=False)
    rsi = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    side = Column(String, nullable=False)



# class User(Base):
#     __tablename__ = 'users'
#
#     class User(Base):
#         __tablename__ = 'users'
#
#         id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#         username = Column(String, unique=True, nullable=False)
#         hashed_password = Column(String, nullable=False)
#         disabled = Column(Boolean, default=False)
#
#         def verify_password(self, password: str) -> bool:
#             """Check if the provided password matches the stored hashed password."""
#             return pwd_context.verify(password, self.hashed_password)
#
#         @classmethod
#         def hash_password(cls, password: str) -> str:
#             """Hash a plain text password."""
#             return pwd_context.hash(password)



# Create all tables
Base.metadata.create_all(engine)

print("Database and tables created successfully.")