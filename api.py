from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import uvicorn
from bot.tools.settings import settings
from bot import bot_control
from passlib.context import CryptContext


load_dotenv(dotenv_path=os.path.abspath('./tools/.env'))

DATABASE_URL = 'postgresql://postgres:admin@localhost:5433/tb'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = "your_secret_key"  # Change this and store in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("password123"),  # Change & store in DB
        "disabled": False,
    }
}

app = FastAPI()



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    return fake_users_db.get(username)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return get_user(fake_users_db, username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import Trade model
from bot.tools.models import Trade, Wallet


# Endpoint to get all trades
@app.get("/trades", response_model=list[dict])
def get_trades(db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
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


@app.get("/wallet")
def get_wallet(db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
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
def get_system_logs(current_user: dict = Depends(get_current_active_user)):
    logs_path = "./logs/system_logs.log"
    try:
        with open(logs_path, "r") as log_file:
            logs = log_file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.get("/error_logs")
def get_system_logs(current_user: dict = Depends(get_current_active_user)):
    logs_path = "./logs/error_logs.log"
    try:
        with open(logs_path, "r") as log_file:
            logs = log_file.readlines()
        return {"error_logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.get("/settings")
def get_settings(current_user: dict = Depends(get_current_active_user)):

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
def clean_wallet(db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
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


def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)