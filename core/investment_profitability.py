import pandas as pd

# Parameters for the new calculation with $50 investment, $350 initial capital, and 15 trades per day
initial_capital = 305
investment_per_trade = 80
profit_per_trade_percentage = 0.18
fee_percentage = 0.32
daily_trades_count = 15
investment_increase_percentage = 0.2
weeks = 16  # 2 weeks
days_in_week = 7
total_days = weeks * days_in_week

# Initialize variables
profits = []
capital = initial_capital
current_investment = investment_per_trade

# Calculate profit over 2 weeks with $50 investment, 15 trades per day, and fees
for day in range(1, total_days + 1):
    if day % days_in_week == 0:  # Increase investment at the end of each week
        current_investment += current_investment * investment_increase_percentage

    gross_profit = current_investment * profit_per_trade_percentage * daily_trades_count
    fee = gross_profit * fee_percentage
    net_profit = gross_profit - fee
    capital += net_profit

    profits.append({
        'Day': day,
        'Gross Profit': gross_profit,
        'Fee': fee,
        'Net Profit': net_profit,
        'Cumulative Capital': capital,
        'Current Investment': current_investment
    })

# Create DataFrame
df = pd.DataFrame(profits)

# Save to Excel
file_path = f'./books/trade_bot_profitability_{weeks}_weeks_{investment_per_trade}_investment_15_trades.xlsx'
df.to_excel(file_path, index=False)


