"""Trade bot indicator settings"""

SYMBOLS = ['ADAUSDT']  # List of cryptos to monitor
INTERVAL = '5m'  # Faster timeframe for scalping (Previously 15m → Now 5m)

ADX_PERIOD = 10  # Faster ADX confirmation (Previously 13 → Now 10)
SHORT_EMA = 9  # Common short EMA for scalping (Previously 5.15 → Now 9)
LONG_EMA = 21  # Classic trend-following EMA (Previously 24.67 → Now 21)

ATR_PERIOD = 7  # Lower ATR period for quick volatility adjustments (Previously 10 → Now 7)
TAKE_PROFIT_ATR = 2.4  # Slightly reduced for faster TP execution (Previously 2.46 → Now 2.0)
STOP_LOSS_ATR = 0.8  # Tighter SL to prevent large drawdowns (Previously 0.75 → Now 0.8)

# Dynamic ATR settings per symbol
ATR_VALUES = {
    'BTCUSDT': 150,
    'ETHUSDT': 100,
    'BNBUSDT': 80,
    'XRPUSDT': 50,
    'ADAUSDT': 40
}  # Adjusted dynamically based on each crypto


CHECKPOINTS = [0.2,
 0.21,
 0.22,
 0.23,
 0.24,
 0.25,
 0.26,
 0.27,
 0.28,
 0.29,
 0.3,
 0.31,
 0.32,
 0.33,
 0.34,
 0.35,
 0.36,
 0.37,
 0.38,
 0.39,
 0.4,
 0.41,
 0.42,
 0.43,
 0.44,
 0.45,
 0.46,
 0.47,
 0.48,
 0.49,
 0.5,
 0.51,
 0.52,
 0.53,
 0.54,
 0.55,
 0.56,
 0.57,
 0.58,
 0.59,
 0.6,
 0.61,
 0.62,
 0.63,
 0.64,
 0.65,
 0.66,
 0.67,
 0.68,
 0.69,
0.7
               ]
