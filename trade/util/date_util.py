import time
from datetime import datetime
from util import log_util

logger = log_util.get_logger()


# 判断当前时间是否在股票交易时间内
# 每天的9:30-11:30 13:00-15:00
def exist_trading_time(debug):
    # if debug:
    #     return True

    now = datetime.now()

    morning_trading_start_time = datetime(now.year, now.month, now.day, 9, 30, 20)
    morning_trading_end_time = datetime(now.year, now.month, now.day, 11, 30, 00)

    afternoon_trading_start_time = datetime(now.year, now.month, now.day, 13, 00, 30)
    afternoon_trading_end_time = datetime(now.year, now.month, now.day, 14, 30, 00)

    if now.__le__(morning_trading_start_time):
        sleep = (morning_trading_start_time - now).total_seconds()
        sleep = 3600 if sleep > 3600 else sleep + 1
        logger.info(f"当前时间不在合法的交易时间内，请稍后再试，暂停{sleep}秒")
        time.sleep(sleep)
    elif now.__ge__(afternoon_trading_end_time):
        logger.info(f"当前时间不在合法的交易时间内，请稍后再试，暂停1小时")
        time.sleep(3600)
    elif now.__ge__(morning_trading_end_time) and now.__le__(afternoon_trading_start_time):
        sleep = (afternoon_trading_start_time - now).total_seconds()
        sleep = 3600 if sleep > 3600 else sleep + 1
        logger.info(f"当前时间不在合法的交易时间内，请稍后再试，暂停{sleep}秒")
        time.sleep(sleep)
    else:
        return True
