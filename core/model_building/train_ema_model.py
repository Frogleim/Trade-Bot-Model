import ccxt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import ta


# Fetch data
symbol = 'MATIC/USDT'
timeframe = '15m'

# Compute EMAs
def compute_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

try:
    data = pd.read_csv(f'./models/data/{symbol}_historical.csv')
except FileNotFoundError:
    exchange = ccxt.binance()
    symbol = 'MATIC/USDT'
    timeframe = '15m'
    since = exchange.parse8601('2020-01-01T00:00:00Z')
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

atr_period = 14
data['ema_short'] = compute_ema(data['close'], span=5)
data['ema_long'] = compute_ema(data['close'], span=8)
data['ATR'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], window=atr_period)

# Define signals
data['signal'] = 0
data.loc[(data['ema_short'] > data['ema_long']) & (data['ATR'] > 0.0026), 'signal'] = 1
data.loc[(data['ema_short'] < data['ema_long']) & (data['ATR'] > 0.0026), 'signal'] = -1

# Split data into features and target
features = ['ema_short', 'ema_long', 'ATR']
target = 'signal'
X = data[features]
y = data[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the model
with open('./models/model/ema_crossover_model.pkl', 'wb') as file:
    pickle.dump(model, file)
