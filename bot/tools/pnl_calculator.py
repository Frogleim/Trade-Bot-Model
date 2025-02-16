
def pnl_calculator(position_size, entry_price, exit_price, side='long', leverage=125):
    position_size_usdt_leverage = position_size * leverage
    if side == 'long':

        roi = (exit_price - entry_price) * (position_size_usdt_leverage / entry_price)
    else:
        roi = (entry_price - exit_price) * (position_size_usdt_leverage / entry_price)
    return roi





if __name__ == '__main__':
    position_size_usdt = 13.29
    leverage_usdt = 75
    entry_price = 664.44
    exit_price = 666.2

    roi = pnl_calculator(
        position_size=position_size_usdt,
        entry_price=entry_price,
        exit_price=exit_price,
    )
    print(roi)