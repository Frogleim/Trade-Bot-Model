from binance.client import Client
import pandas as pd


class Binance:
    def __init__(self):
        self.api_key = ''
        self.api_secret = ''
        self.client = Client()

    def download_binance_futures_data(self, symbol, interval, start_date, end_date, filename):
        """
        Downloads historical futures data from Binance and saves it to a CSV file.

        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param interval: Kline interval (e.g., '1m', '5m', '15m', '1h', '1d')
        :param start_date: Start date in 'YYYY-MM-DD' format
        :param end_date: End date in 'YYYY-MM-DD' format
        :param filename: Output CSV filename
        """
        klines = self.client.futures_historical_klines(symbol, interval, start_date, end_date)
        columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ]
        df = pd.DataFrame(klines, columns=columns)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    # Example Usage


if __name__ == '__main__':
    mybinance = Binance()
    mybinance.download_binance_futures_data(symbol="BTCUSDT", interval="5m", start_date="2024-01-01", end_date="2024-01-30",
                                   filename="binance_futures_data.csv")