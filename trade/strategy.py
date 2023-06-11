import storage


def is_buy(symbol, name, latest_price, change, high, open, yesterday_close, debug):
    if debug:
        return (3.4 < change < 6) and (not name.startswith("N")) and (not storage.is_bought(symbol)) and (storage.select_buy_times(symbol) < 2)
    else:
        return (open / yesterday_close < 1.08) and (3.4 < change < 6) and (high / latest_price < 1.005) \
               and (not name.startswith("N")) \
               and (not storage.is_bought(symbol)) \
               and (storage.select_buy_times(symbol) < 2)


def is_sell(buy_change, sell_change, high_change, debug):
    if debug:
        return True
    if sell_change < 3 \
            or (buy_change - sell_change > 0.50) \
            or (high_change - sell_change > 0.50):
        return True