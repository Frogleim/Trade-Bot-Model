def calculate_future_wallet(initial_balance, daily_profit_percent, trades_per_day, days):
    """
    Calculate the future wallet balance based on profit percentage, trades per day, and number of days.

    Parameters:
        initial_balance (float): Starting wallet balance.
        daily_profit_percent (float): Average profit percentage per trade.
        trades_per_day (int): Number of trades made per day.
        days (int): Number of days for projection.

    Returns:
        float: Projected wallet balance after the specified number of days.
    """
    balance = initial_balance

    for day in range(1, days + 1):
        daily_profit_factor = (1 + daily_profit_percent / 100) ** trades_per_day
        balance *= daily_profit_factor  # Compound profits for each trade in the day

        print(f"Day {day}: ${balance:.2f}")

    return balance


# Example usage
initial_balance = float(input("Enter your initial wallet balance: "))
daily_profit_percent = float(input("Enter your average profit percentage per trade: "))
trades_per_day = int(input("Enter the number of trades you make per day: "))
days = int(input("Enter the number of days for projection: "))

future_wallet = calculate_future_wallet(initial_balance, daily_profit_percent, trades_per_day, days)
print(f"\nProjected wallet balance after {days} days: ${future_wallet:.2f}")
