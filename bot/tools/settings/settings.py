"""Trade bot indicator settings"""

SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']  # List of cryptos to monitor
INTERVAL = '5m'  # Faster timeframe for scalping (Previously 15m → Now 5m)

ADX_PERIOD = 14  # Faster ADX confirmation (Previously 13 → Now 10)
SHORT_EMA = 6  # Common short EMA for scalping (Previously 5.15 → Now 9)
LONG_EMA = 21  # Classic trend-following EMA (Previously 24.67 → Now 21)

ATR_PERIOD = 7  # Lower ATR period for quick volatility adjustments (Previously 10 → Now 7)
TAKE_PROFIT_ATR = 2.5 # Slightly reduced for faster TP execution (Previously 2.46 → Now 2.0)
STOP_LOSS_ATR = 1  # Tighter SL to prevent large drawdowns (Previously 0.75 → Now 0.8)

# Dynamic ATR settings per symbol
ATR_VALUES = {
    'BTCUSDT': 150,
    'ETHUSDT': 100,
    'BNBUSDT': 80,
    'XRPUSDT': 50,
    'ADAUSDT': 40
}  # Adjusted dynamically based on each crypto