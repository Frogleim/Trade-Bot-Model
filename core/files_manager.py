import pandas as pd
import os

# Specify the file path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "core")
file_path = f"{files_dir}/files/data.csv"


def insert_data(entry_price, close_price, profit, entry_price_diff):
    # Read the existing data from the CSV file
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # If the file doesn't exist, create a new DataFrame
        df = pd.DataFrame(columns=["entry price", "close price", "profit", "entry price difference"])

    # Create a new row with the given data
    new_data = {
        "entry price": entry_price,
        "close price": close_price,
        "profit": profit,
        "entry price difference": entry_price_diff
    }

    # Append the new data to the DataFrame
    df = df.append(new_data, ignore_index=True)

    # Write the updated data back to the CSV file
    df.to_csv(file_path, index=False)


# Example usage
if __name__ == '__main__':
    insert_data(150, 110, 10, 10)