import sys
import time
from datetime import datetime
import efinance as ef
import pandas as pd
import traceback
from loguru import logger
import chinese_calendar
import os

os.environ['NO_PROXY'] = '*'

# logger
logger.add('api_log.log', encoding='utf-8')

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)


#     债券代码  债券名称    涨跌幅      最新价       最高       最低      今开     涨跌额      换手率     量比 动态市盈率      成交量           成交额    昨日收盘         总市值        流通市值      行情ID 市场类型
# 0    123051  今天转债  24.03   158.66    165.0    134.0   134.0   30.74   496.74  67.16     -  1388341  2185911136.0  127.92   443443594   443443594  0.123051   深A
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
        kzz_top = kzz_sort[:70].copy()
        # 重新设置下标
        kzz_top.index = range(len(kzz_top))
        return kzz_top
    except:
        logger.error(traceback.format_exc())

    return pd.DataFrame()


# 判断当前时间是否在股票交易时间内
# 每天的9:30-11:30 13:00-15:00
def on_trading_time(now_time):
    morning_trading_start_time = datetime(now_time.year, now_time.month, now_time.day, 9, 30, 00)
    morning_trading_end_time = datetime(now_time.year, now_time.month, now_time.day, 11, 30, 00)

    afternoon_trading_start_time = datetime(now_time.year, now_time.month, now_time.day, 13, 00, 30)
    afternoon_trading_end_time = datetime(now_time.year, now_time.month, now_time.day, 15, 00, 00)

    if now_time.__le__(morning_trading_start_time):
        sleep = (morning_trading_start_time - now_time).total_seconds()
        sleep = 3600 if sleep > 3600 else sleep + 1
    elif now_time.__ge__(afternoon_trading_end_time):
        sleep = -1
    elif now_time.__ge__(morning_trading_end_time) and now_time.__le__(afternoon_trading_start_time):
        sleep = (afternoon_trading_start_time - now_time).total_seconds()
        sleep = 3600 if sleep > 3600 else sleep + 1
    else:
        sleep = 0

    return sleep


def download():
    kzz_top = get_kzz_realtime_top()
    if not kzz_top.empty:
        kzz_top_copy = kzz_top[['债券代码', '债券名称', '涨跌幅', '最新价', '最高', '最低', '今开', '成交量', '成交额', '昨日收盘']]
        kzz_top_copy.insert(0, "时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        kzz_top_copy.to_csv(file_name, mode='a', index=None, header=False)
    else:
        time.sleep(20)


if __name__ == '__main__':
    logger.info("start**********************************************")
    if not os.path.exists('./data'):
        os.mkdir("data")

    today = datetime.now()
    if not chinese_calendar.is_workday(today) or today.isoweekday() > 5:
        sys.exit()

    file_name = f"./data/{today.strftime('%Y%m%d')}.csv"

    while True:
        _now_time = datetime.now()
        sleep_time = on_trading_time(_now_time)
        if sleep_time < 0:
            break
        elif sleep_time > 0:
            time.sleep(sleep_time)
        else:
            download()
            time.sleep(1)
