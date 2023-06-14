import efinance as ef
import pandas as pd
import ths_trader as ths
import traceback
import time
import config
import message
from util import date_util
from util import log_util
from datetime import datetime
import os
import storage

os.environ['NO_PROXY'] = '*'

# logger
logger = log_util.get_logger()

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

# 是否调试
debug = config.fast_trade_debug_mode

today = datetime.now().strftime("%Y%m%d")


def get_kzz_realtime_top():
    try:
        # 获取可转债实时行情
        kzz_spot = ef.bond.get_realtime_quotes()
        # 数据中的-替换成-100
        kzz_spot["涨跌幅"].replace(r'-', "-100", inplace=True)
        # 将列类型转换成float便于排序
        kzz_spot['涨跌幅'] = kzz_spot['涨跌幅'].astype(float)
        # 按涨跌幅排序
        kzz_sort = kzz_spot.sort_values(by="涨跌幅", ascending=False)
        # 取出前50
        kzz_top_50 = kzz_sort[:50].copy()
        # 重新设置下标
        kzz_top_50.index = range(len(kzz_top_50))
        return kzz_top_50
    except:
        logger.error(traceback.format_exc())

    return pd.DataFrame()


def calculate_change(price, yesterday_close):
    return round(((price / yesterday_close) - 1) * 100, 5)


def send_dingding_msg(trade_type, now, latest_price, change, name, symbol):
    if 'buy'.__eq__(trade_type):
        msg = "操作:【😊】买入 \n时间:%s \n代码:%s \n名称:%s \n价格:%s \n买入涨幅:%s" % (
            now, symbol, name, latest_price, change)
    else:
        msg = "操作:【😂】卖出 \n时间:%s \n代码:%s \n名称:%s \n价格:%s \n卖出涨幅:%s" % (
            now, symbol, name, latest_price, change)

    message.send(msg)


#    债券代码 债券名称  涨跌幅   最新价    最高    最低    今开     涨跌额    换手率  量比 动态市盈率 成交量     成交额      昨日收盘    总市值     流通市值      行情ID   市场类型      更新时间         最新交易日
# 0  113669  N景23转  20.25  120.245  123.8  120.01  122.71  20.245  27.14    -     -    313216  380234522.0  100.000      -      1387627300  1.113669   沪A  2023-05-09 16:11:31  2023-05-09
# 1  123193  海能转债  16.32  116.324  118.5  115.46  118.0   16.324  60.69    -     -    364142  423652515.31 100.000  697944000  697944000   0.123193   深A  2023-05-09 15:34:18  2023-05-09
# 2  123018  溢利转债   5.53   258.55  261.0  241.0   244.53  13.539  401.89  2.71   -    217567  554910131.02 245.011  139969404  139969404   0.123018   深A  2023-05-09 15:34:30  2023-05-09

def buy_kzz(kzz_realtime_top):
    # 遍历筛选
    for row in kzz_realtime_top.itertuples():
        symbol = getattr(row, '债券代码')
        name = getattr(row, '债券名称')
        high = float(getattr(row, '最高'))
        change = getattr(row, '涨跌幅')
        open_price = float(getattr(row, '今开'))
        yesterday_close = float(getattr(row, '昨日收盘'))
        latest_price = float(getattr(row, '最新价'))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_buy(symbol, name, latest_price, change, high, open_price, yesterday_close):
            logger.info("【start】============================================================================")
            logger.info("【😊】开始买入，当前kzz实时行情信息:\n【😊】" + row.__str__())

            ths_trader.buy_fast(symbol)
            logger.info("【😊】交易完成！")

            storage.insert_buy_info(symbol, name, latest_price, change, now, yesterday_close)
            logger.info('【😊】通知：在[%s]时委托下单，以市价[%s][%s]涨幅买入[%s][%s]股票' % (
                now, latest_price, change, name, symbol))

            send_dingding_msg("buy", now, latest_price, change, name, symbol)
            logger.info("【end】============================================================================")
            break


def sell_kzz():
    kzz_position_list = storage.select_position_list()
    if not kzz_position_list:
        return

    kzz_position_dict_list = dict()
    for x in kzz_position_list:
        kzz_position_dict_list[x["symbol"]] = x

    for row in kzz_top.itertuples():
        symbol = getattr(row, '债券代码')
        if not kzz_position_dict_list.__contains__(symbol):
            continue

        name = getattr(row, '债券名称')
        latest_price = float(getattr(row, '最新价'))
        change = getattr(row, '涨跌幅')
        high = getattr(row, '最高')
        buy_change = kzz_position_dict_list[symbol]["buy_change"]
        buy_time = datetime.strptime(kzz_position_dict_list[symbol]["buy_time"], "%Y-%m-%d %H:%M:%S")
        yesterday_close = kzz_position_dict_list[symbol]["yesterday_close"]
        high_change = calculate_change(high, yesterday_close)
        now = datetime.now()
        now_format_str = now.strftime("%Y-%m-%d %H:%M:%S")

        if is_sell(buy_change, change, high_change, buy_time, now):
            logger.info("【start】************************************************************************************")
            logger.info("【😂】开始卖出，当前kzz实时行情信息:\n【😂】" + row.__str__())

            ths_trader.sell_fast(symbol)
            logger.info("【😂】交易完成！")

            storage.insert_sell_info(symbol, 0, latest_price, change, now_format_str)
            logger.info('【😂】通知：在[%s]时委托下单，以市价[%s][%s]涨幅卖出[%s][%s]股票' % (
                now_format_str, latest_price, change, name, symbol))

            send_dingding_msg("sell", now_format_str, latest_price, change, name, symbol)
            logger.info("【end】************************************************************************************")


def is_buy(symbol, name, latest_price, change, high, open_price, yesterday_close):
    if debug:
        return (3 < change < 8) and (not name.startswith("N")) and (not storage.is_bought(symbol)) and (storage.select_buy_times(symbol) < 2)
    else:
        return (open_price / yesterday_close < 1.08) and (3 < change < 8) and (high / latest_price < 1.009) \
               and (not name.startswith("N")) \
               and (not storage.is_bought(symbol)) \
               and (storage.select_buy_times(symbol) < 2)


def is_sell(buy_change, sell_change, high_change, buy_time, sell_time):
    if debug:
        return True
    if buy_change - sell_change > 3 or sell_change < 2:
        return True

    if (sell_time - buy_time).seconds < 350:
        return False

    if sell_change < 3 \
            or (buy_change - sell_change > 0.40) \
            or (high_change - sell_change > 0.40):
        return True


if __name__ == '__main__':
    ths_trader = ths.ThsTrader()
    ths_trader.cancel_if_auto_code()

    while True:
        kzz_top = get_kzz_realtime_top()
        if kzz_top.empty:
            time.sleep(60)
            continue

        if date_util.exist_trading_time(config.trade_time_debug_mode):
            try:
                buy_kzz(kzz_top[:10].copy())
                sell_kzz()
                time.sleep(1)
            except:
                logger.error(traceback.format_exc())
                time.sleep(30)
