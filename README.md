# Miya 

## Trading Bot

Automated Trading Bot for Binance Platform

Our fully automated trading bot for the Binance platform leverages up to 10 technical indicators, ensuring a robust and efficient trading experience.

## Requirements

```sh
python-binance
pandas
ccxt
fastapi
uvicorn
matplotlib
flask
dash
plotly
tradingpattern
colorama
psycopg2
websocket-client

```

## Installation

```sh
pip install -r requirements.txt
```

then run API for setuping your binance api credentials

```sh
uvicorn main:app --reload
```
it will run ``FastAPI`` on host ``localhost:8000``. Send your Binance API Key and API Secret with endpoint : `` curl -X 'POST' \
  'http://127.0.0.1:8000/set_credentials/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "api_key": "api_key",
  "api_secret": "api_secret"
}' ``

## Runing
Before running set trade bot configurations with api - ``curl -X 'POST' \
  'http://127.0.0.1:8000/set_trade_coins/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "symbol": "MATICUSDT",
  "quantity": 33,
  "checkpoints": [0.001, 0.0014, 0.0016, 0.0018, 0.0050, 0.0060, 0.0070, 0.0080, 0.0090, 0.0099]
}'``
In this example I use ``MATICUSDT``. quantity is position size, and checkpoints is profit checkpoints
Bot working with 3 technical indicators, such as - ``MACD``, ``Bollinger Bands`` and ``Dual Thrust``.
For running bot , it should run two ``py`` files. 
1. ``python3 web.py`` - which is signal 24/7 checker
2. ``python3 bot.py`` - which is bot for opening and close possition with signals
