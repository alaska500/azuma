import efinance as ef
import pandas as pd
from util import log_util
from datetime import datetime, timedelta
import os
import back_model

os.environ['NO_PROXY'] = '*'

# logger
logger = log_util.get_logger()

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)


def calculate_change(price, yesterday_close):
    return round(((price / yesterday_close) - 1) * 100, 5)


def is_buy(symbol, name, latest_price, change, high, strategy):
    return (strategy.buy__change_floor < change < strategy.buy_change_upper) and (high / latest_price < 1.009) \
           and (not name.startswith("N")) \
           and (not strategy.back_storage.is_bought(symbol)) \
           and (strategy.back_storage.select_buy_times(symbol) < 3)


def back_buy(top_10, strategy):
    for row in top_10.itertuples():
        trade_time = getattr(row, "时间")
        symbol = getattr(row, "债券代码")
        name = getattr(row, "债券名称")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")

        if is_buy(symbol, name, latest_price, change, high, strategy):
            quote = ef.bond.get_quote_history(str(symbol), beg=strategy.back_yesterday, end=strategy.back_yesterday)
            yesterday_close = quote.loc[0, '收盘']
            strategy.back_storage.insert_buy_info(symbol, name, latest_price, change, trade_time, yesterday_close)


def back_sell(seconds_tick_data, strategy):
    kzz_position_list = trade_strategy.back_storage.select_position_list()
    if not kzz_position_list:
        return

    kzz_position_dict_list = dict()
    for x in kzz_position_list:
        kzz_position_dict_list[x["symbol"]] = x

    for row in seconds_tick_data.itertuples():
        symbol = str(getattr(row, '债券代码'))
        index = getattr(row, "Index")
        if not kzz_position_dict_list.__contains__(symbol):
            continue

        trade_time = getattr(row, "时间")
        name = getattr(row, "债券名称")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")
        buy_change = kzz_position_dict_list[symbol]["buy_change"]
        yesterday_close = kzz_position_dict_list[symbol]["yesterday_close"]
        high_change = calculate_change(high, yesterday_close)
        buy_time = datetime.strptime(kzz_position_dict_list[symbol]["buy_time"], "%Y-%m-%d %H:%M:%S")
        sell_time = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S")

        if is_sell(index, buy_change, change, high_change, buy_time, sell_time, strategy):
            strategy.back_storage.insert_sell_info(symbol, round(change - buy_change, 5), latest_price, change,
                                                   trade_time)


def is_sell(index, buy_change, sell_change, high_change, buy_time, sell_time, strategy):
    # 止损2% 或者涨幅低于2.5%
    if buy_change - sell_change > 3 or sell_change < 2:
        return True

    # 买入之后等待5分钟之后再卖出
    if (sell_time - buy_time).seconds < strategy.wait_time:
        return False

    # 涨幅榜前2手动卖出
    # if index < 2 and (sell_time - buy_time).seconds < 1800:
    #     return False

    # 常规止盈止损
    if sell_change < strategy.stop_loss_lowest \
            or (buy_change - sell_change > strategy.stop_loss) \
            or (high_change - sell_change > strategy.stop_profit):
        return True


def back_test(strategy):
    back_date = strategy.back_date
    df = pd.read_csv(f"E:/script/{back_date}.csv", header=None)
    df.columns = ["时间", '债券代码', '债券名称', '涨跌幅', '最新价', '最高', '最低', '今开', '成交量', '成交额',
                  '昨日收盘']

    start = 0
    step = 50
    while True:
        end = start + step
        seconds_tick_data = df[start:end].copy()
        if seconds_tick_data.empty:
            break
        start = end
        print(f"====================================={start}")
        back_buy(seconds_tick_data[:10], strategy)
        back_sell(seconds_tick_data, strategy)

    strategy.income = strategy.back_storage.select_income()


if __name__ == '__main__':
    back_test_date_list = ["20230613", "20230614"]
    strategy_list = []
    for back_date_str in back_test_date_list:
        back_test_date = datetime.strptime(back_date_str, "%Y%m%d")
        yesterday = (back_test_date + timedelta(days=-1)).strftime("%Y%m%d")
        # buy__change_floor, buy_change_upper, stop_profit, stop_loss, stop_loss_lowest, wait_time
        strategy_list.append(back_model.TradeStrategyV2(3, 10, 0.4, 0.4, 2.5, 350, back_date_str, yesterday))


        #strategy_list.append(back_model.TradeStrategyV2(3.5, 8, 0.4, 0.5, 2.5, 300, back_date_str, yesterday))
        #strategy_list.append(back_model.TradeStrategyV2(3, 10, 0.4, 0.5, 2.5, 300, back_date_str, yesterday))
        #strategy_list.append(back_model.TradeStrategyV2(3.5, 10, 0.4, 0.5, 2.5, 300, back_date_str, yesterday))

    for trade_strategy in strategy_list:
        back_test(trade_strategy)

    for trade_strategy in strategy_list:
        logger.info(f"over 策略：{trade_strategy.table_name} 收益：{round(trade_strategy.income, 6)}")
