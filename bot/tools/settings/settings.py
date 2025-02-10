"""Trade bot indicator settings"""

SYMBOL = 'BTCUSDT'
INTERVAL = '5m'  # Faster timeframe for scalping (Previously 15m → Now 5m)

ADX_PERIOD = 10  # Faster ADX confirmation (Previously 13 → Now 10)
SHORT_EMA = 9  # Common short EMA for scalping (Previously 5.15 → Now 9)
LONG_EMA = 21  # Classic trend-following EMA (Previously 24.67 → Now 21)

ATR_PERIOD = 7  # Lower ATR period for quick volatility adjustments (Previously 10 → Now 7)
TAKE_PROFIT_ATR = 2.0  # Slightly reduced for faster TP execution (Previously 2.46 → Now 2.0)
STOP_LOSS_ATR = 0.8  # Tighter SL to prevent large drawdowns (Previously 0.75 → Now 0.8)
ATR = 150  # Adjusted to be more dynamic based on shorter timeframe movements