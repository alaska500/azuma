import akshare as ak
import pandas as pd
import ths_trader as ths
import traceback
import time
import storage
from datetime import datetime
from loguru import logger
from threading import Thread
import global_value
import message

# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8', filter=lambda record: record["level"].name == "INFO")

# 当天已经交易过的股票
dealt = storage.read_dealt_stock()
dealt.add("not null")

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

# 是否调试
debug = global_value.fast_trade_debug



def get_kzz_daily_20():
    while True:
        try:
            # 获取可转债实时行情
            kzz_spot = ak.bond_zh_hs_cov_spot()
            kzz_spot['rise'] = kzz_spot.changepercent.astype('float')

            # 取涨幅前10
            kzz_sort = kzz_spot.sort_values(by="rise", ascending=False)
            global_value.pd = kzz_sort[:20].copy()
            global_value.pd.index = range(len(global_value.pd))
            # logger.info("可转债信息\t" + kzz_top_20)
            # logger.info("kzz数据采集成功" + global_value.pd.to_string())
        except Exception as ex:
            logger.error(traceback.format_exc())
            time.sleep(10)

def kzz_trade(ths_trader):

    if global_value.pd.empty:
        logger.info("暂时没有收集到数据，暂停5s后重试")
        return

    kzz_top_copy = global_value.pd.copy()

    # 遍历筛选
    for index, row in kzz_top_copy.iterrows():

        name = row["name"]
        symbol = row["symbol"]
        # 昨天收盘价
        settlement = float(row["settlement"])
        high = float(row["high"])

        # 获取转债的最新价格
        kzz_min_df = ak.bond_zh_hs_cov_min(symbol=symbol, period='1', adjust='')
        latest_price = kzz_min_df.loc[kzz_min_df.index[-1], '最新价']
        rise = ((latest_price / settlement) - 1) * 100

        if is_start_trade(latest_price, rise, high, name, symbol, debug):
            logger.info("=====================================================================================")
            #logger.info("\n" + row.values.__str__())
            logger.info("\n 实时数据：[{}][{}] 最新价:[{}] 涨幅:[{}] 昨收:[{}] 今开:[{}] 最高:[{}] 最低:[{}] tick:[{}]", name, symbol, row["trade"], row["changepercent"], row["settlement"], row["open"], row["high"], row["low"], row["ticktime"])
            logger.info("\n" + kzz_min_df.iloc[-1:].to_string())
            start_trade(ths_trader, symbol, name, latest_price, rise)
            add_dealt_stock(symbol)
            new = '通知：在[%s]时委托下单，以市价[%s]买入[%s][%s]股票[100]手' % (datetime.now(), latest_price, name, symbol)
            logger.info(new)
            message.send_dingding_msg(new)
            kzz_top_copy.loc[index, "haha"] = str(latest_price) + " ✔"
            logger.info("=====================================================================================")
            break
        else:
            kzz_top_copy.loc[index, "haha"] = str(latest_price) + " ❌"

    # logger.trace("查看可转债实时top行情")
    # logger.trace("\n {}", kzz_top_copy.to_string())


def is_start_trade(latest_price, rise, high, name, symbol, debug):

    if debug:
        return (3 < rise < 5) and (not name.startswith("N")) and (not dealt.__contains__(symbol))
    else:
        return (3 < rise < 5) and (high / latest_price < 1.007) and (not name.startswith("N")) and (
            not dealt.__contains__(symbol))


def start_trade(ths_trader, symbol, name, trade, rise):
    logger.info("准备交易，查找到符合条件的可转债[{}][{}] 价格[{}] 涨幅[{}]", symbol, name, trade, rise)
    ths_trader.market_buy_fast(symbol[2:], 100)
    logger.info("交易完成！")


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
    t = Thread(target=get_kzz_daily_20, args=())
    t.start()

    ths_trader = ths.ThsTarder()
    ths_trader.cancel_if_auto_code()

    while True:
        if in_trading_time(debug):
            try:
                kzz_trade(ths_trader)
                time.sleep(3)
            except Exception as ex:
                logger.error(traceback.format_exc())
                time.sleep(10)
