import time
import traceback
from util import MyTT
import efinance as ef
import pandas as pd
from util import log_util
from datetime import datetime, timedelta
from util import cache_util
import os
import back_model

os.environ['NO_PROXY'] = '*'

# logger
logger = log_util.get_logger()

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

memory_cache = cache_util.MemoryCache()


def get_quote_daily_history(symbol, beg, end, klt):
    key = f"{symbol}_{beg}_{klt}"
    result = memory_cache.get_value(key)
    if not result is None:
        return result

    try:
        quote = ef.bond.get_quote_history(symbol, beg=beg, end=end, klt=klt)
        memory_cache.set_value(key, quote, 3600)
        return quote
    except:
        logger.info(traceback.format_exc())
        time.sleep(10)
        return get_quote_daily_history(symbol, beg, end, klt)


def get_min_line(symbol, trade_date):
    file_name = f"E:/script/min/{trade_date}/min/{symbol}.csv"
    if not os.path.exists(file_name):
        print(f"kzz {symbol} {trade_date} 分时线不存在")
        return None
    return pd.read_csv(file_name, header=0, index_col=0)


def calculate_change(price, yesterday_close):
    return round(((price / yesterday_close) - 1) * 100, 5)


def get_quote_min_history(symbol, trade_day):
    key = f"{symbol}_{trade_day}"
    result = memory_cache.get_value(key)
    if not result is None:
        return result

    quote_min_list = get_min_line(symbol, trade_day)
    if quote_min_list is None:
        return None
    memory_cache.set_value(key, quote_min_list, 3600)
    return quote_min_list


def macd(symbol, trade_time, latest_price):
    trade_day = trade_time.strftime("%Y%m%d")
    trade_time_temp = trade_time.strftime("%Y-%m-%d %H:%M")
    quote_history = get_quote_min_history(str(symbol), trade_day)
    if quote_history is None:
        return None

    quote_list = pd.DataFrame()
    quote_filter = quote_history.loc[quote_history['时间'] < trade_time_temp]
    quote_list["时间"] = quote_filter["时间"]
    quote_list["收盘"] = quote_filter["收盘"]
    # 在实盘时候不用加入latest_price, get_quote_history返回最后一行会是最新价格
    # quote_list.loc[len(quote_list.index)] = latest_price
    quote_list['DIF'], quote_list['DEA'], quote_list['MACD'] = MyTT.MACD(quote_list["收盘"])
    return quote_list


def macd_gold_fork(symbol, trade_time, latest_price):
    quote_list = macd(symbol, trade_time, latest_price)
    if quote_list is None:
        return False

    quote_len = len(quote_list)
    if quote_len == 0 or quote_len == 1:
        return True
    elif quote_len == 2 and quote_len == 3:
        if quote_list.iloc[len(quote_list.index) - 1, 3] < 0:
            return False
    else:
        m2 = quote_list.iloc[len(quote_list.index) - 2, 4]
        m3 = quote_list.iloc[len(quote_list.index) - 1, 4]
        if m2 < m3 and m3 > 0:
            return True


def exceed_deadline(trade_time):
    deadline = datetime(trade_time.year, trade_time.month, trade_time.day, 14, 50, 00)
    if trade_time < deadline:
        return True


def buy_gap(symbol, trade_time, strategy):
    buy_info = strategy.back_storage.select_latest_buy(symbol)
    if buy_info is None:
        return True
    latest_sell_time = buy_info["sell_time"]
    sell_time = datetime.strptime(latest_sell_time, "%Y-%m-%d %H:%M:%S")
    if (trade_time - sell_time).seconds < 30:
        return False
    return True


def is_buy(symbol, name, trade_time, latest_price, change, high, strategy):
    buy = (strategy.buy__change_floor < change < strategy.buy_change_upper) \
           and exceed_deadline(trade_time) \
           and (high / latest_price < 1.005) \
           and (not name.startswith("N")) \
           and (not strategy.back_storage.is_bought(symbol)) \
           and (strategy.back_storage.select_income_by_symbol(str(symbol)) > -0.5) \
           and strategy.back_storage.select_buy_times(symbol) < 2 \
           and macd_gold_fork(symbol, trade_time, latest_price) \
           and buy_gap(symbol, trade_time, strategy)
    if buy:
        return buy
    return buy


def back_buy(top_10, strategy):
    for row in top_10.itertuples():
        rank = getattr(row, "Index")
        trade_time = getattr(row, "时间")
        symbol = getattr(row, "债券代码")
        name = getattr(row, "债券名称")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")
        yesterday_close = getattr(row, "昨日收盘")
        turn_volume = round(getattr(row, "成交额"))
        buy_time = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S")

        if is_buy(symbol, name, buy_time, latest_price, change, high, strategy):
            strategy.back_storage.insert_buy_info(symbol, name, rank, turn_volume, latest_price, change, trade_time,
                                                  yesterday_close)


def back_sell(seconds_tick_data, strategy):
    kzz_position_list = trade_strategy.back_storage.select_position_list()
    if not kzz_position_list:
        return

    kzz_position_dict_list = dict()
    for x in kzz_position_list:
        kzz_position_dict_list[x["symbol"]] = x

    for row in seconds_tick_data.itertuples():
        symbol = str(getattr(row, '债券代码'))
        if not kzz_position_dict_list.__contains__(symbol):
            continue

        index = getattr(row, "Index")
        trade_time = getattr(row, "时间")
        latest_price = getattr(row, "最新价")
        change = getattr(row, "涨跌幅")
        high = getattr(row, "最高")
        primary_id = kzz_position_dict_list[symbol]["id"]
        buy_change = kzz_position_dict_list[symbol]["buy_change"]
        buy_time = kzz_position_dict_list[symbol]["buy_time"]
        yesterday_close = kzz_position_dict_list[symbol]["yesterday_close"]
        highest_rank = kzz_position_dict_list[symbol]["highest_rank"]
        high_change = calculate_change(high, yesterday_close)
        sell_time = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S")

        if index < highest_rank:
            strategy.back_storage.update_highest_rank(primary_id, index)

        if is_sell(symbol, latest_price, buy_time, index, buy_change, change, high_change, sell_time):
            income = round(change - buy_change, 5)
            strategy.back_storage.insert_sell_info(symbol, income, latest_price, change, trade_time, index)


def macd_dead_fork(symbol, buy_time, trade_time, latest_price):
    seconds = trade_time.strftime("%S")
    if seconds.__eq__("05") or seconds.__eq__("25") or seconds.__eq__("45"):
        quote_list = macd(symbol, trade_time, latest_price)
        if quote_list is None:
            return True

        quote_len = len(quote_list)
        if quote_len == 0 or quote_len == 1:
            return False
        elif quote_len == 2 or quote_len == 3:
            if quote_list.iloc[len(quote_list.index) - 1, 3] < 0:
                return True
        else:

            m3_time = quote_list.iloc[len(quote_list.index) - 1, 0]
            buy_time_min = buy_time[:-2] + "00"
            if m3_time < buy_time_min or buy_time_min.endswith("13:00:00"):
                return False

            dif3 = quote_list.iloc[len(quote_list.index) - 3, 2]
            dif2 = quote_list.iloc[len(quote_list.index) - 2, 2]
            dif1 = quote_list.iloc[len(quote_list.index) - 2, 2]
            macdd = quote_list.iloc[len(quote_list.index) - 1, 4]

            if dif3 > dif2 > dif1 or macdd < 0:
                return True


            # buy_index = quote_list.loc[quote_list['时间'] == buy_time_min].index.tolist()[0]
            #
            # if len(quote_list.index) - 2 == buy_index or len(quote_list.index) - 1 == buy_index:
            #     if m3 < m2:
            #         return True
            #
            # if m2 > m3 or m3 < 0:
            #     return True


def is_sell(symbol, latest_price, buy_time, index, buy_change, sell_change, high_change, sell_time):
    end_time = sell_time.strftime("%H:%M:%S")
    if end_time > "14:55:00":
        logger.info(f"{symbol}卖出uuu 买入涨幅:{buy_change} 卖出涨幅:{sell_change} 最高涨幅:{high_change} index:{index}")
        return True

    # 止损2% 或者涨幅低于2.5%
    if buy_change - sell_change > 1.5 or sell_change < 1 or index > 8:
        logger.info(f"{symbol}卖出ooo 买入涨幅:{buy_change} 卖出涨幅:{sell_change} 最高涨幅:{high_change} index:{index}")
        return True

    if macd_dead_fork(symbol, buy_time, sell_time, latest_price) and abs(buy_change - sell_change) > 0.4:
        logger.info(f"{symbol}卖出kkk 买入涨幅:{buy_change} 卖出涨幅:{sell_change} 最高涨幅:{high_change} index:{index}")
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
        seconds_tick_data = df[start:end].copy(deep=True)
        if seconds_tick_data.empty:
            break
        start = end
        print(f"====================================={start}")
        seconds_tick_data.index = range(len(seconds_tick_data))
        # seconds_tick_data_filter = seconds_tick_data[:strategy.top_n].loc[seconds_tick_data["债券代码"] == 127080]
        # if seconds_tick_data_filter.empty:
        #     print("seconds_tick_data_filter.empty")
        # back_buy(seconds_tick_data_filter, strategy)
        back_buy(seconds_tick_data[:strategy.top_n].copy(deep=True), strategy)
        back_sell(seconds_tick_data, strategy)

    strategy.income = strategy.back_storage.select_income()

# 卖出用dif试试
if __name__ == '__main__':
    # back_test_date_list = ["20230613", "20230614", "20230615", "20230616"]
    # back_test_date_list = [ "20230614"]
    back_test_date_list = ["20230621"]
    strategy_list = []
    for back_date_str in back_test_date_list:
        back_test_date = datetime.strptime(back_date_str, "%Y%m%d")
        yesterday = (back_test_date + timedelta(days=-1)).strftime("%Y%m%d")
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 10))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 9))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 8))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 7))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 6))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 5))
        # strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 4))
        strategy_list.append(back_model.TradeStrategyV2(3, 16, 0.5, 0.5, 2.5, 280, back_date_str, yesterday, 3))

    for trade_strategy in strategy_list:
        try:
            back_test(trade_strategy)
        except:
            logger.info(traceback.format_exc())

    for trade_strategy in strategy_list:
        logger.info(f"over 策略：{trade_strategy.table_name} 收益：{round(trade_strategy.income, 6)}")
