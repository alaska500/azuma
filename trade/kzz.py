import akshare as ak
import pandas as pd
import ths_trader as ths
import traceback
import time
import storage
from datetime import datetime
from loguru import logger

# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8')



pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', 200)

# 是否调试
debug = False


def kzz_trade():
    # 获取可转债实时行情
    kzz_spot = ak.bond_zh_hs_cov_spot()
    kzz_spot['rise'] = kzz_spot.changepercent.astype('float')

    # 取涨幅前10
    kzz_sort = kzz_spot.sort_values(by="rise", ascending=False)
    kzz_top = kzz_sort[:20].copy()

    # 遍历筛选
    for index, row in kzz_top.iterrows():

        rise = row["rise"]
        high = float(row["high"])
        trade = float(row["trade"])
        name = row["name"]
        symbol = row["symbol"]

        if is_start_trade(rise, high, trade, name, symbol, debug):
            start_trade(symbol, name, trade, rise)
            add_dealt_stock(symbol)
            kzz_top.loc[index, "haha"] = "✔"
            break
        else:
            kzz_top.loc[index, "haha"] = "❌"

    logger.info("查看可转债实时top10行情")
    logger.info("\n {}", kzz_top.to_string())


def is_start_trade(rise, high, trade, name, symbol, debug):
    if debug:
        return (3 < rise < 7) and (not name.startswith("N")) and (not dealt.__contains__(symbol))
    else:
        return (3 < rise < 6) and (high / trade < 1.005) and (not name.startswith("N")) and (not dealt.__contains__(symbol))


def start_trade(symbol, name, trade, rise):
    logger.info("=====================================================================================")
    logger.info("准备交易，查找到符合条件的可转债[{}][{}] 价格[{}] 涨幅[{}]", symbol, name, trade, rise)
    ths.stock_trade(symbol[2:], name, trade)
    logger.info("交易完成！")
    logger.info("=====================================================================================")


def add_dealt_stock(sybmol):
    dealt.add(sybmol)
    storage.save_dealt_stock(sybmol)


def in_trading_time(debug):
    if debug:
        return True

    now = datetime.now()

    morning_trading_start_time = datetime(now.year, now.month, now.day, 9, 31, 30)
    morning_trading_end_time = datetime(now.year, now.month, now.day, 11, 30, 00)

    afternoon_trading_start_time = datetime(now.year, now.month, now.day, 13, 00, 30)
    afternoon_trading_end_time = datetime(now.year, now.month, now.day, 14, 58, 00)

    if now.__le__(morning_trading_start_time):
        logger.info("当前时间不在合法的交易时间内，请稍后再试")
        sleep = (morning_trading_start_time - now).total_seconds()
        time.sleep(3600 if sleep > 3600 else sleep)
    elif now.__ge__(afternoon_trading_end_time):
        logger.info("当前时间不在合法的交易时间内，请稍后再试")
        time.sleep(3600)
    elif now.__ge__(morning_trading_end_time) and now.__le__(afternoon_trading_start_time):
        logger.info("当前时间不在合法的交易时间内，请稍后再试")
        sleep = (afternoon_trading_start_time - now).total_seconds()
        time.sleep(3600 if sleep > 3600 else sleep)
    else:
        return True


if __name__ == '__main__':
    while True:
        if in_trading_time(debug):
            try:
                kzz_trade()
            except Exception as ex:
                logger.error(traceback.format_exc())
                time.sleep(10)
