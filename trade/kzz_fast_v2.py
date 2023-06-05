import efinance as ef
import pandas as pd
import ths_trader as ths
import traceback
import time
import storage
import global_variable
import message
from util import date_util
from util import log_util
from datetime import datetime
import os

os.environ['NO_PROXY'] = '*'

# logger
logger = log_util.get_logger()

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

trade_storage = storage.TradeStorage()

# 是否调试
debug = global_variable.fast_trade_debug_mode

date = datetime.now().strftime("%Y%m%d")

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
        kzz_top = kzz_sort[:50].copy()
        # 重新设置下标
        kzz_top.index = range(len(kzz_top))
        return kzz_top
    except Exception:
        logger.error(traceback.format_exc())

    return pd.DataFrame()


def send_dingding_msg(type, now, latest_price, change, name, symbol):

    if 'buy'.__eq__(type):
        msg = "操作:【😊】买入 \n时间:%s \n代码:%s \n名称:%s \n价格:%s \n买入涨幅:%s" % (now, symbol, name, latest_price, change)
    else:
        msg = "操作:【😂】卖出 \n时间:%s \n代码:%s \n名称:%s \n价格:%s \n卖出涨幅:%s" % (now, symbol, name, latest_price, change)

    message.send(msg)


def confirm_buy(symbol):
    time.sleep(5)
    df = ef.bond.get_quote_history(str(symbol), beg=date)[-1:]
    name = df.loc[0, '债券名称']
    latest_price = df.loc[0, '收盘']
    high = df.loc[0, '最高']
    change = df.loc[0, '涨跌幅']
    confirm = is_start_trade(latest_price, change, high, name, symbol, debug)
    logger.info(f"【😀】当前kzz {name} 涨跌幅[{change}] 确认是否继续买入：{confirm}")
    return confirm


def confirm_sell(symbol):
    time.sleep(5)
    df = ef.bond.get_quote_history(str(symbol), beg=date)[-1:]
    name = df.loc[0, '债券名称']
    latest_price = df.loc[0, '收盘']
    change = df.loc[0, '涨跌幅']
    confirm = is_sell(symbol, datetime.now(), latest_price, change)
    logger.info(f"【😂】当前kzz {name} 涨跌幅[{change}] 确认是否继续卖出：{confirm}")
    return confirm

#    债券代码 债券名称  涨跌幅   最新价    最高    最低    今开     涨跌额    换手率  量比 动态市盈率 成交量     成交额      昨日收盘    总市值     流通市值      行情ID   市场类型      更新时间         最新交易日
# 0  113669  N景23转  20.25  120.245  123.8  120.01  122.71  20.245  27.14    -     -    313216  380234522.0  100.000      -      1387627300  1.113669   沪A  2023-05-09 16:11:31  2023-05-09
# 1  123193  海能转债  16.32  116.324  118.5  115.46  118.0   16.324  60.69    -     -    364142  423652515.31 100.000  697944000  697944000   0.123193   深A  2023-05-09 15:34:18  2023-05-09
# 2  123018  溢利转债   5.53   258.55  261.0  241.0   244.53  13.539  401.89  2.71   -    217567  554910131.02 245.011  139969404  139969404   0.123018   深A  2023-05-09 15:34:30  2023-05-09

def buy_kzz(ths_trader, kzz_realtime_top):
    # 遍历筛选
    for row in kzz_realtime_top.itertuples():
        symbol = getattr(row, '债券代码')
        name = getattr(row, '债券名称')
        high = float(getattr(row, '最高'))
        latest_price = float(getattr(row, '最新价'))
        change = getattr(row, '涨跌幅')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_start_trade(latest_price, change, high, name, symbol, debug):
            logger.info("【😊】============================================================================")
            logger.info("【😊】开始买入，当前kzz实时行情信息:\n【😊】" + row.__str__())
            if not confirm_buy(symbol):
                break
            ths_trader.buy_fast(symbol)
            logger.info("【😊】交易完成！")
            trade_storage.insert_bought_position(symbol, name, now, latest_price, change)
            new = '【😊】通知：在[%s]时委托下单，以市价[%s][%s]涨幅买入[%s][%s]股票' % (
                now, latest_price, change, name, symbol)
            logger.info(new)
            send_dingding_msg("buy", now, latest_price, change, name, symbol)
            logger.info("【😊】============================================================================")
            break


def sell_kzz(ths_trader, kzz_top):

    for row in kzz_top.itertuples():
        symbol = getattr(row, '债券代码')
        name = getattr(row, '债券名称')
        latest_price = float(getattr(row, '最新价'))
        change = getattr(row, '涨跌幅')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if symbol in trade_storage.bought_set and symbol not in trade_storage.sold_set:
            if is_sell(symbol, now, latest_price, change):
                logger.info("【😂】************************************************************************************")
                logger.info("【😂】开始卖出，当前kzz实时行情信息:\n【😂】" + row.__str__())
                if not confirm_sell(symbol):
                    break
                ths_trader.sell_fast(symbol)
                logger.info("【😂】交易完成！")
                trade_storage.insert_sold_position(symbol, now, latest_price, change)
                new = '【😂】通知：在[%s]时委托下单，以市价[%s][%s]涨幅卖出[%s][%s]股票' % (
                    now, latest_price, change, name, symbol)
                logger.info(new)
                send_dingding_msg("sell", now, latest_price, change, name, symbol)
                logger.info("【😂】************************************************************************************")


def is_start_trade(latest_price, change, high, name, symbol, debug):
    if debug:
        return (3.3 < change < 5.5) and (not name.startswith("N")) and (not trade_storage.bought_set.__contains__(symbol))
    else:
        return (3.3 < change < 5.5) and (high / latest_price < 1.009) and (not name.startswith("N")) and (
            not trade_storage.bought_set.__contains__(symbol))


def is_sell(symbol, sell_time, sell_price, sell_change):
    buy_df = trade_storage.get_position(symbol)
    buy_change = buy_df['买入时涨幅']
    if sell_change < 2.70 or buy_change - sell_change > 0.75:
        return True


if __name__ == '__main__':
    ths_trader = ths.ThsTrader()
    ths_trader.cancel_if_auto_code()

    while True:
        kzz_top = get_kzz_realtime_top()
        if kzz_top.empty:
            time.sleep(10)
            continue

        if date_util.exist_trading_time(debug):
            try:
                buy_kzz(ths_trader, kzz_top[:6].copy())
                sell_kzz(ths_trader, kzz_top)
                time.sleep(1)
            except Exception:
                logger.error(traceback.format_exc())
                time.sleep(10)
