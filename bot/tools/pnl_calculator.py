
def pnl_calculator(position_size, entry_price, exit_price, side='long', leverage=125):
    position_size_usdt_leverage = position_size * leverage
    if side == 'long':

        roi = (exit_price - entry_price) * (position_size_usdt_leverage / entry_price)
    else:
        roi = (entry_price - exit_price) * (position_size_usdt_leverage / entry_price)
    return roi





if __name__ == '__main__':
    position_size_usdt = 40
    leverage_usdt = 10
    entry_price = 50000
    exit_price = 56000

    roi = pnl_calculator(position_size_usdt, leverage_usdt, entry_price, exit_price)
    print(roi)