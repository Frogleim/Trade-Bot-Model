import pandas as pd

# Load the trade data from the uploaded CSV file
file_path = './6fc3f94c-5676-11ef-81b8-0e3291b69067-1.csv'
trade_data = pd.read_csv(file_path)

# Display the first few rows of the data to understand its structure
trade_data.head()

# Calculate basic metrics
total_trades = trade_data.shape[0]
winning_trades = trade_data[trade_data['Closing PNL'] > 0]
losing_trades = trade_data[trade_data['Closing PNL'] <= 0]

# Metrics
num_winning_trades = winning_trades.shape[0]
num_losing_trades = losing_trades.shape[0]
win_rate = num_winning_trades / total_trades
loss_rate = num_losing_trades / total_trades
average_profit = winning_trades['Closing PNL'].mean()
average_loss = losing_trades['Closing PNL'].mean()
total_profit = winning_trades['Closing PNL'].sum()
total_loss = losing_trades['Closing PNL'].sum()
profit_factor = total_profit / abs(total_loss)

# Create a summary of the metrics
metrics_summary = {
    "Total Trades": total_trades,
    "Winning Trades": num_winning_trades,
    "Losing Trades": num_losing_trades,
    "Win Rate": win_rate,
    "Loss Rate": loss_rate,
    "Average Profit per Trade": average_profit,
    "Average Loss per Trade": average_loss,
    "Total Profit": total_profit,
    "Total Loss": total_loss,
    "Profit Factor": profit_factor,
}

import ace_tools as tools; tools.display_dataframe_to_user(name="Trade Metrics Summary", dataframe=pd.DataFrame([metrics_summary]))

print(metrics_summary)
