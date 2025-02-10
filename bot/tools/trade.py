import time
from dotenv import load_dotenv
from .socket_binance import get_last_price
from . import loggs
from .settings import settings

# Load environment variables
load_dotenv(dotenv_path="./tools/.env")

# Global constants
CHECK_INTERVAL = 1  # Time in seconds between price checks

# Define checkpoint fractions (customize as desired)
CHECKPOINTS = [0.2, 0.3, 0.4, 0.5, 0.75]  # e.g., update stop loss at 50% and 75% of the profit target

def calculate_trade_targets(entry_price: float, atr: float, is_long: bool) -> tuple[float, float]:
    take_profit_multiplier = settings.TAKE_PROFIT_ATR
    stop_loss_multiplier = settings.STOP_LOSS_ATR

    if is_long:
        target_price = entry_price + (take_profit_multiplier * atr)
        stop_loss = entry_price - (stop_loss_multiplier * atr)
    else:
        target_price = entry_price - (take_profit_multiplier * atr)
        stop_loss = entry_price + (stop_loss_multiplier * atr)

    return target_price, stop_loss

def monitor_trade(entry_price: float, target_price: float, stop_loss: float, is_long: bool) -> tuple[str, float, float]:
    """
    Monitors the trade and checks price updates until target or stop-loss is hit.
    Also updates the stop loss based on checkpoints.
    """
    trade_type = "Long" if is_long else "Short"
    loggs.system_log.info(f"{trade_type} trade started: Entry Price: {entry_price}, Target: {target_price}, Stop Loss: {stop_loss}")

    # Use a variable to track the current (dynamic) stop loss
    current_stop_loss = stop_loss

    while True:
        try:
            current_price = get_last_price(settings.SYMBOL)
        except Exception as e:
            loggs.system_log.error(f"Error fetching price: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        loggs.system_log.info(f"Entry: {entry_price}, Target: {target_price}, Current: {current_price}, Stop Loss: {current_stop_loss}")

        # Check if a checkpoint is hit and update the stop loss accordingly
        if is_long:
            profit_distance = target_price - entry_price
            for fraction in CHECKPOINTS:
                checkpoint_price = entry_price + fraction * profit_distance
                # Only update if the current price has reached or exceeded the checkpoint
                # and the new checkpoint is higher than the current stop loss
                if current_price >= checkpoint_price and checkpoint_price > current_stop_loss:
                    loggs.system_log.info(f"Long trade checkpoint reached at {checkpoint_price}. Updating stop loss from {current_stop_loss} to {checkpoint_price}.")
                    current_stop_loss = checkpoint_price
        else:
            profit_distance = entry_price - target_price  # For a short trade
            for fraction in CHECKPOINTS:
                checkpoint_price = entry_price - fraction * profit_distance
                if current_price <= checkpoint_price and checkpoint_price < current_stop_loss:
                    loggs.system_log.info(f"Short trade checkpoint reached at {checkpoint_price}. Updating stop loss from {current_stop_loss} to {checkpoint_price}.")
                    current_stop_loss = checkpoint_price

        # Check if the target is hit
        if (is_long and current_price >= target_price) or (not is_long and current_price <= target_price):
            loggs.system_log.info(f"{trade_type} trade finished successfully with profit")
            pnl = abs(target_price - entry_price)
            return "Profit", pnl, target_price

        # Check if the (updated) stop loss is hit
        if (is_long and current_price <= current_stop_loss) or (not is_long and current_price >= current_stop_loss):
            loggs.system_log.info(f"{trade_type} trade finished with a loss (or stopped out after checkpoint)")
            pnl = -abs(current_stop_loss - entry_price)
            return "Loss", pnl, current_stop_loss

        time.sleep(CHECK_INTERVAL)

def long_trade(entry_price: float, atr: float) -> tuple[str, float, float]:
    """Executes and monitors a long (buy) trade."""
    loggs.system_log.warning(f"Buy position placed successfully: Entry Price: {entry_price}")
    target_price, stop_loss = calculate_trade_targets(entry_price, atr, is_long=True)
    return monitor_trade(entry_price, target_price, stop_loss, is_long=True)

def short_trade(entry_price: float, atr: float) -> tuple[str, float, float]:
    """Executes and monitors a short (sell) trade."""
    loggs.system_log.warning(f"Sell position placed successfully: Entry Price: {entry_price}")
    target_price, stop_loss = calculate_trade_targets(entry_price, atr, is_long=False)
    return monitor_trade(entry_price, target_price, stop_loss, is_long=False)

if __name__ == "__main__":
    # Example execution; you can change parameters as needed.
    trade_result, atr_value, pnl = short_trade(96620, 300)
    print(f"Result: {trade_result}, ATR: {atr_value}, PnL: {pnl}")