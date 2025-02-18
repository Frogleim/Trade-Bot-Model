from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
loaded = load_dotenv(dotenv_path=os.path.abspath('./tools/.env'))
print(f"Dotenv loaded: {loaded}")

# Database credentials
DB_USER = "postgres"
DB_PASS = "admin"
DB_HOST = "pgdb"  # This is the container name in Docker Compose
DB_PORT = "5432"
DB_NAME = "tb"

# Create an engine for the default `postgres` database
default_engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres")

# Check if the database exists before creating it
with default_engine.connect() as connection:
    result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"))
    exists = result.scalar()

    if not exists:
        connection.execute(text(f"CREATE DATABASE {DB_NAME}"))
        connection.commit()
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


# Create all tables
Base.metadata.create_all(engine)

print("Database and tables created successfully.")