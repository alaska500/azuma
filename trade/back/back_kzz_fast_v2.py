import efinance as ef
import pandas as pd
from util import log_util
from datetime import datetime
import os
import back_storage
import back_model
from back_storage import BackStorage

os.environ['NO_PROXY'] = '*'

# logger
logger = log_util.get_logger()

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)


def calculate_change(price, yesterday_close):
    return round(((price / yesterday_close) - 1) * 100, 5)


def is_buy(symbol, name, latest_price, change, high):
    return (strategy.buy__change_floor < change < strategy.buy_change_upper) and (high / latest_price < 1.005) \
           and (not name.startswith("N")) \
           and (not strategy.back_storage.is_bought(symbol)) \
           and (strategy.back_storage.select_buy_times(symbol) < 2)


def is_sell(buy_change, sell_change, high_change):
    if sell_change < strategy.stop_loss_lowest \
            or (buy_change - sell_change > strategy.stop_loss) \
            or (high_change - sell_change > strategy.stop_profit):
        return True


def back_buy(top_10):
    for row in top_10.itertuples():
        date = getattr(row, "时间")
        symbol = getattr(row, "债券代码")
        name = getattr(row, "债券名称")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")

        if is_buy(symbol, name, latest_price, change, high):
            quote = ef.bond.get_quote_history(str(symbol), beg='20230612', end='20230612')
            yesterday_close = quote.loc[0, '收盘']
            strategy.back_storage.insert_buy_info(symbol, name, latest_price, change, date, yesterday_close)
            logger.info('【😂】通知：在[%s]时委托下单，以市价[%s][%s]涨幅买入[%s][%s]股票' % (
                date, latest_price, change, name, symbol))


def back_sell():
    kzz_position_list = strategy.back_storage.select_position_list()
    if not kzz_position_list:
        return

    kzz_position_dict_list = dict()
    for x in kzz_position_list:
        kzz_position_dict_list[x["symbol"]] = x

    for row in seconds_tick_data.itertuples():
        symbol = str(getattr(row, '债券代码'))

        if not kzz_position_dict_list.__contains__(symbol):
            continue

        date = getattr(row, "时间")
        name = getattr(row, "债券名称")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")
        buy_change = kzz_position_dict_list[symbol]["buy_change"]
        buy_time = kzz_position_dict_list[symbol]["buy_time"]
        yesterday_close = kzz_position_dict_list[symbol]["yesterday_close"]
        high_change = calculate_change(high, yesterday_close)
        start_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if (end_time - start_time).seconds < strategy.wait_time:
            continue

        if is_sell(buy_change, change, high_change):
            strategy.back_storage.insert_sell_info(symbol, round(change - buy_change, 5), latest_price, change, date)
            logger.info('【😂】通知：在[%s]时委托下单，以市价[%s][%s]涨幅卖出[%s][%s]股票' % (
                date, latest_price, change, name, symbol))


if __name__ == '__main__':
    date_str = datetime.now().strftime("%Y_%m_%d")
    tabel_name = f"back_trade_{date_str}_3_8_001"
    # buy__change_floor, buy_change_upper, stop_profit, stop_loss, stop_loss_lowest, wait_time, table_name
    strategy = back_model.TradeStrategyV2(3, 8, 0.4, 0.4, 3, 300, tabel_name, BackStorage(tabel_name))

    df = pd.read_csv("E:/script/2023-06-13_copy.csv", header=None)
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
        back_buy(seconds_tick_data[:10])
        back_sell()
