from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables
load_dotenv(dotenv_path=os.path.abspath('./tools/.env'))

# Database URL
DATABASE_URL = 'postgresql://postgres:admin@pgdb:5432/tb'

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import Trade model
from bot.tools.models import Trade

# Endpoint to get all trades
@app.get("/trades", response_model=list[dict])
def get_trades(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    if not trades:
        raise HTTPException(status_code=404, detail="No trades found")
    return [{
        "id": trade.id,
        "symbol": trade.symbol,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "pnl": trade.pnl,
        "long_ema": trade.long_ema,
        "short_ema": trade.short_ema,
        "adx": trade.adx,
        "atr": trade.atr,
        "rsi": trade.rsi,
        "volume": trade.volume,
        "side": trade.side
    } for trade in trades]

# Endpoint to get system logs
@app.get("/system_logs")
def get_system_logs():
    logs_path = "./logs/system_logs.log"
    try:
        with open(logs_path, "r") as log_file:
            logs = log_file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.get("/error_logs")
def get_system_logs():
    logs_path = "./logs/error_logs.log"
    try:
        with open(logs_path, "r") as log_file:
            logs = log_file.readlines()
        return {"error_logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)