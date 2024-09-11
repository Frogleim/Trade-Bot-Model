import requests
import numpy as np
from binance.client import Client
from datetime import datetime
import pytz  # For timezone handling

client = Client()

SYMBOL = "BTCUSDT"
TIME_PERIOD = "5m"
LIMIT = "200"
QNTY = 0.006

# Define Yerevan timezone
yerevan_tz = pytz.timezone('Asia/Yerevan')


# Custom function to calculate the Exponential Moving Average (EMA)
def calculate_ema(data, period):
    ema = []
    k = 2 / (period + 1)  # smoothing constant
    ema.append(np.mean(data[:period]))  # take the first EMA value as the mean of the first period values
    for price in data[period:]:
        ema_value = (price - ema[-1]) * k + ema[-1]
        ema.append(ema_value)
    return np.array(ema)


def place_order(order_type):
    if order_type == "buy":
        order = client.create_order(symbol=SYMBOL, side="buy", quantity=QNTY, type="MARKET")
    else:
        order = client.create_order(symbol=SYMBOL, side="sell", quantity=QNTY, type="MARKET")

    print("Order placed successfully!")
    print(order)
    return


def log_signal(signal_type):
    # Get current time in Yerevan timezone
    now = datetime.now(yerevan_tz)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Open the file in append mode and write the signal
    with open("signals.txt", "a") as f:
        f.write(f"{timestamp} - {signal_type} signal for {SYMBOL}\n")

    print(f"Logged {signal_type} signal at {timestamp}")


def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
    res = requests.get(url)
    return_data = []
    for each in res.json():
        return_data.append(float(each[4]))
    return np.array(return_data)


def main():
    buy = False
    sell = True
    ema_8 = None
    ema_21 = None

    last_ema_8 = None
    last_ema_21 = None

    print("started running..")
    while True:
        closing_data = get_data()
        print('No signal at this moment')
        ema_8 = calculate_ema(closing_data, 5)[-1]
        ema_21 = calculate_ema(closing_data, 13)[-1]

        if ema_8 > ema_21 and last_ema_8:
            if last_ema_8 < last_ema_21 and not buy:
                print("Buy signal")
                log_signal("Buy")  # Log the buy signal with Yerevan time
                buy = True
                sell = False

        if ema_21 > ema_8 and last_ema_21:
            if last_ema_21 < last_ema_8 and not sell:
                print("Sell signal")
                log_signal("Sell")  # Log the sell signal with Yerevan time
                sell = True
                buy = False

        last_ema_8 = ema_8
        last_ema_21 = ema_21


if __name__ == "__main__":
    main()
