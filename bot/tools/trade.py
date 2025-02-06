import time
from dotenv import load_dotenv
from .socket_binance import get_last_price
import settings
from . import loggs

# Load environment variables
load_dotenv(dotenv_path="./tools/.env")


# Global constants
CHECK_INTERVAL = 1  # Time in seconds between price checks


def calculate_trade_targets(entry_price: float, atr: float, is_long: bool) -> tuple[float, float]:
    take_profit_multiplier = settings.TAKE_PROFIT_ATR
    stop_loss_multiplier = settings.STOP_LOSS_ATR

    if is_long:
        target_price = entry_price + (take_profit_multiplier * atr)
        stop_loss = entry_price - (stop_loss_multiplier * atr)
    else:
        target_price = entry_price - (take_profit_multiplier * atr)  # Correct for short trades
        stop_loss = entry_price + (stop_loss_multiplier * atr)  # Correct for short trades

    return target_price, stop_loss

def monitor_trade(entry_price: float, target_price: float, stop_loss: float, is_long: bool) -> tuple[str, float, float]:
    """
    Monitors the trade and checks price updates until target or stop-loss is hit.
    """
    trade_type = "Long" if is_long else "Short"
    loggs.system_log.info(f"{trade_type} trade started: Entry Price: {entry_price}, Target: {target_price}, Stop Loss: {stop_loss}")

    while True:
        try:
            current_price = get_last_price(settings.SYMBOL)
        except Exception as e:
            loggs.system_log.error(f"Error fetching price: {e}")
            time.sleep(CHECK_INTERVAL)
            continue

        loggs.system_log.info(f"Entry: {entry_price}, Target: {target_price}, Current: {current_price}, Stop Loss: {stop_loss}")

        if (is_long and current_price >= target_price) or (not is_long and current_price <= target_price):
            loggs.system_log.info(f"{trade_type} trade finished successfully with profit")
            return "Profit", abs(target_price - entry_price), target_price

        if (is_long and current_price <= stop_loss) or (not is_long and current_price >= stop_loss):
            loggs.system_log.info(f"{trade_type} trade finished with a loss")
            return "Loss", -abs(stop_loss - entry_price), stop_loss

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
    trade_result, atr_value, pnl = short_trade(96620, 300)
    print(f"Result: {trade_result}, ATR: {atr_value}, PnL: {pnl}")