from decimal import Decimal


# Function to calculate the PnL
def calculate_pnl(entry_price, close_price, quantity, position_side, leverage=1):
    """
    Calculate PnL for futures trading.

    :param entry_price: The price at which the trade was entered.
    :param close_price: The price at which the trade was closed.
    :param quantity: The number of contracts or amount of asset traded.
    :param position_side: 'LONG' or 'SHORT', depending on the trade direction.
    :param leverage: The leverage used in the trade (default is 1 for no leverage).
    :return: The calculated PnL.
    """
    entry_price = Decimal(entry_price)
    close_price = Decimal(close_price)
    quantity = Decimal(quantity)

    if position_side.upper() == 'LONG':
        pnl = (close_price - entry_price) * quantity * leverage
    elif position_side.upper() == 'SHORT':
        pnl = (entry_price - close_price) * quantity * leverage
    else:
        raise ValueError("Position side must be either 'LONG' or 'SHORT'")

    return pnl


# Example usage
if __name__ == "__main__":
    # Example input
    entry_price = input("Enter entry price: ")
    close_price = input("Enter close price: ")
    quantity = input("Enter quantity: ")
    position_side = input("Enter position side (LONG or SHORT): ")
    leverage = input("Enter leverage (default 1): ")

    # Use default leverage if input is empty
    leverage = Decimal(leverage) if leverage else 1

    # Calculate PnL
    pnl = calculate_pnl(entry_price, close_price, quantity, position_side, leverage)

    print(f"PnL for the trade: {pnl}")
