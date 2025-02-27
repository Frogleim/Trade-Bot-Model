from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from bot.tools.settings import settings
from bot import bot_control

# Load environment variables
load_dotenv(dotenv_path='.env')

# Database URL

DATABASE_URL = 'postgresql://postgres:admin@localhost:5433/tb'

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app
app = FastAPI(
    debug=True,
    title='Hedge.ai',
    version='0.1.1',
    description='The Trading Bot API provides a set of endpoints for managing and analyzing cryptocurrency trading strategies. It allows users to retrieve market signals, execute trades, monitor market trends, and backtest strategies using technical indicators like EMA, ADX, ATR, and RSI. This API is designed to work with Binance Futures and integrates with RabbitMQ for real-time signal processing.',
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import Trade model
from bot.tools.models import Trade, Wallet


@app.get("/get-columns", response_model=list[str])
def get_trade_columns(db: Session = Depends(get_db)):
    """Returns a list of all column names in the Trade table."""
    return [column.name for column in Trade.__table__.columns]


# Endpoint to get all trades
@app.get("/trades", response_model=list[dict])
def get_trades(db: Session = Depends(get_db)):
    try:
        trades = db.query(Trade).all()

        if not trades:
            raise HTTPException(status_code=404, detail="No trades found")
        return [{
            "trade_id": trade.trade_id,
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
            "side": trade.side,
            "start_time": trade.start_time,
            "end_time": trade.end_time,
        } for trade in trades]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wallet")
def get_wallet(db: Session = Depends(get_db)):
    wallet_data = db.query(Wallet).all()
    if not wallet_data:
        raise HTTPException(status_code=404, detail="No wallet found")
    return [{
        "initial balance": wallet.id,
        "roi": wallet.roi,
        "final_balance": wallet.final_balance

    } for wallet in wallet_data]

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


@app.get("/settings")
def get_settings():

    config = {
        "SYMBOL": settings.SYMBOLS,
        "INTERVAL": settings.INTERVAL,
        "ADX_PERIOD": settings.ADX_PERIOD,
        "SHORT_EMA": settings.SHORT_EMA,
        "LONG_EMA": settings.LONG_EMA,
        "ATR_PERIOD": settings.ATR_PERIOD,
        "TAKE_PROFIT_ATR": settings.TAKE_PROFIT_ATR,
        "STOP_LOSS_ATR": settings.STOP_LOSS_ATR,
    }
    return config


@app.post("/clean-wallet")
def clean_wallet(db: Session = Depends(get_db)):
    wallet = db.query(Wallet).all()
    if not wallet:
        raise HTTPException(status_code=404, detail="No wallet found")
    for wallet in wallet:
        db.delete(wallet)
        db.commit()
    return {"success": True}


@app.post("/pause-bot/")
def pause_bot():
    """Pauses the bot"""
    return bot_control.pause_bot()

@app.post("/unpause-bot/")
def unpause_bot():
    """Unpauses the bot"""
    return bot_control.unpause_bot()

@app.post("/stop-bot/")
def stop_bot():
    """Stops the bot completely"""
    return bot_control.stop_bot()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080, reload=True)