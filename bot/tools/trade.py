import time
from dotenv import load_dotenv
from .socket_binance import get_last_price
from . import loggs
from .settings import settings


load_dotenv(dotenv_path="./tools/.env")
CHECK_INTERVAL = 1
CHECKPOINTS = [0.4, 0.5, 0.75]

def calculate_trade_targets(entry_price: float, atr: float, is_long: bool, symbol: str) -> tuple[float, float]:
    take_profit_multiplier = settings.TAKE_PROFIT_ATR
    stop_loss_multiplier = settings.STOP_LOSS_ATR
    if symbol == 'BNBUSDT' or symbol == 'ADAUSDT':
        if is_long:
            target_price = entry_price + (take_profit_multiplier * atr)
            stop_loss = entry_price - (atr / stop_loss_multiplier)
        else:  # Short trade for BTCUSDT
            target_price = entry_price - (take_profit_multiplier * atr)
            stop_loss = entry_price + (atr / stop_loss_multiplier)
    else:  # Other assets
        if is_long:
            target_price = entry_price + (take_profit_multiplier * atr)
            stop_loss = entry_price - (stop_loss_multiplier * atr)
        else:  # Short trade for non-BTCUSDT assets
            target_price = entry_price - (take_profit_multiplier * atr)
            stop_loss = entry_price + (stop_loss_multiplier * atr)

    return target_price, stop_loss


def monitor_trade(symbol: str, entry_price: float, target_price: float, stop_loss: float, is_long: bool) ->\
        tuple[str, float, float, str]:
    """
    Monitors the trade and checks price updates until target or stop-loss is hit.
    Also updates the stop loss based on checkpoints.
    """
    trade_type = "Long" if is_long else "Short"
    loggs.system_log.info(f"{trade_type} trade started for {symbol}: Entry Price: {entry_price},"
                          f" Target: {target_price}, Stop Loss: {stop_loss}")

    current_stop_loss = stop_loss
    while True:
        try:
            current_price = get_last_price(symbol)
        except Exception as e:
            loggs.system_log.error(f"Error fetching price for {symbol}: {e}")
            time.sleep(CHECK_INTERVAL)
            continue
        loggs.system_log.info(f"{symbol} - Entry: {entry_price}, Target: {target_price},"
                              f" Current: {current_price}, Stop Loss: {current_stop_loss}")
        if is_long:
            profit_distance = target_price - entry_price
            for fraction in CHECKPOINTS:
                checkpoint_price = entry_price + fraction * profit_distance
                if current_price >= checkpoint_price and checkpoint_price > current_stop_loss:
                    loggs.system_log.info(f"{symbol} - Long trade checkpoint reached at {checkpoint_price}."
                                          f" Updating stop loss from {current_stop_loss} to {checkpoint_price}.")
                    current_stop_loss = checkpoint_price
        else:
            profit_distance = entry_price - target_price
            for fraction in CHECKPOINTS:
                checkpoint_price = entry_price - fraction * profit_distance
                if current_price <= checkpoint_price and checkpoint_price < current_stop_loss:
                    loggs.system_log.info(f"{symbol} - Short trade checkpoint reached at {checkpoint_price}."
                                          f" Updating stop loss from {current_stop_loss} to {checkpoint_price}.")
                    current_stop_loss = checkpoint_price
        if (is_long and current_price >= target_price) or (not is_long and current_price <= target_price):
            loggs.system_log.info(f"{symbol} - {trade_type} trade finished successfully with profit")
            pnl = (target_price - entry_price) if is_long else (entry_price - target_price)
            return "Profit", pnl, target_price, symbol

        if (is_long and current_price <= current_stop_loss) or (not is_long and current_price >= current_stop_loss):
            loggs.system_log.info(
                f"{symbol} - {trade_type} trade finished with a loss (or stopped out after checkpoint)")
            pnl = (current_stop_loss - entry_price) if is_long else (entry_price - current_stop_loss)
            return "Loss", pnl, current_stop_loss, symbol

        time.sleep(CHECK_INTERVAL)

def execute_trade(symbol: str, entry_price: float, atr: float, is_long: bool) -> tuple[str, float, float, str]:
    """Executes and monitors a trade for the given symbol."""
    trade_type = "Long" if is_long else "Short"
    loggs.system_log.warning(f"{symbol} - {trade_type} position placed successfully: Entry Price: {entry_price}")
    target_price, stop_loss = calculate_trade_targets(entry_price, atr, is_long, symbol)
    return monitor_trade(symbol, entry_price, target_price, stop_loss, is_long)

if __name__ == "__main__":
    symbols = settings.SYMBOLS  # Monitor multiple cryptos
    for symbol in symbols:
        trade_result, pnl, exit_price, traded_symbol = execute_trade(symbol, 96620, 300, is_long=False)
        print(f"{traded_symbol} - Result: {trade_result}, PnL: {pnl}, Exit Price: {exit_price}")
