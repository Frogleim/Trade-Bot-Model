# Trade Bot

## Overview
This Trade Bot is a FastAPI-based application combined with a trading bot that interacts with a PostgreSQL database to store and retrieve trading data. It also provides system logs for monitoring and makes automated trade decisions based on EMA crossover strategy, ADX, RSI, ATR, and volume analysis.

## Features
- Fetch trading data from a PostgreSQL database
- Retrieve system logs from the `./logs/system_log.logs` file
- Automated trading bot that executes trades based on predefined strategies
- API endpoints built with FastAPI
- Docker support for easy deployment

## Requirements
- Python 3.11+
- PostgreSQL
- Docker (optional for containerized deployment)

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Frogleim/Trade-Bot-Model.git
   cd Trade-Bot-Model
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the environment variables in `.env` file (if applicable):
   ```env
   DATABASE_URL=postgresql://postgres:admin@localhost:5433/tb
   ATR_PERIOD=14
   ```

## Running the Application
### Locally
Start the API:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

Start the Bot:
```sh
python bot/main.py
```

### With Docker
1. Build and start the services using Docker Compose:
   ```sh
   docker-compose up --build
   ```

## API Endpoints
### Get All Trades
**Endpoint:** `GET /trades`

**Response:**
```json
[
    {
        "id": 1,
        "symbol": "BTC/USD",
        "entry_price": 45000.0,
        "exit_price": 46000.0,
        "pnl": 1000.0,
        "long_ema": 45500.0,
        "short_ema": 45800.0,
        "adx": 25.5,
        "atr": 300.0,
        "rsi": 60.2,
        "volume": 5000.0,
        "side": "buy"
    }
]
```

### Get System Logs
**Endpoint:** `GET /system_logs`

**Response:**
```json
{
    "logs": [
        "2025-02-05 12:00:00 - Trade executed: BTC/USD Buy 1.5 BTC",
        "2025-02-05 12:05:00 - Trade closed: BTC/USD Sell 1.5 BTC"
    ]
}
```

## Trading Bot
The bot fetches market data using Binance API and applies the following trading strategy:
- **EMA Crossover:** Identifies bullish and bearish crossovers for trade signals.
- **ADX Confirmation:** Ensures strong trends before making a trade.
- **RSI Filter:** Confirms if the asset is in a good buying or selling range.
- **ATR for Volatility:** Ensures market has sufficient volatility.
- **Volume Confirmation:** Uses historical volume to confirm trend strength.

The bot determines whether to go `long`, `short`, or `hold` based on the strategy.

## Docker Compose Configuration
The project uses the following `docker-compose.yml` setup:
```yaml
version: '3.9'

services:
  bot:
    env_file:
      - ./bot/tools/.env
    build:
      context: ./bot
    volumes:
      - tools:/logs
    restart: always

  api:
    env_file:
      - ./bot/tools/.env
    build:
      context: .
    volumes:
      - tools:/logs
    ports:
      - "8000:8000"
    restart: always

  db:
    image: "postgres:16"
    hostname: 'pgdb'
    ports:
      - 5432:5432
    environment:
      - POSTGRES_DB=tb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=admin
    container_name: bot_db
    volumes:
      - pgdbdata:/var/lib/postgresql/data/
    restart: always

volumes:
  coins_trade:
  pgdbdata:
  tools:
  restarting:
```

## Contributing
Feel free to submit issues and pull requests for improvements.

## License
This project is licensed under the MIT License.

