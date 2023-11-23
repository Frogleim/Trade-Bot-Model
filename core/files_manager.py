import pandas as pd
import os

# Specify the file path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "core")
file_path = f"{files_dir}/files/model_dataset.csv"


def insert_data(entry_price, close_price, profit, entry_price_diff=0.0, open_time=None, close_time=None):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # If the file doesn't exist, create a new DataFrame
        df = pd.DataFrame(columns=["entry price", "close price", "profit", "entry price difference", 'open_time', 'close_time'])
    new_data = {
        "entry price": round(float(entry_price), 1),
        "close price": round(float(close_price), 1),
        "profit": round(float(profit), 1),
        "entry price difference": round(float(entry_price_diff), 1),
        "open_time": open_time,
        "close_time": close_time
    }
    df = df.append(new_data, ignore_index=True)
    df.to_csv(file_path, index=False)


# Example usage
if __name__ == '__main__':
    insert_data(150, 110, 10, 10)
