import akshare as ak
import pandas as pd
import traceback
import time
from datetime import datetime
from loguru import logger
from MyTT import *
import matplotlib.pyplot as plt

# logger
logger.add('../../logs/back_{time}.log', rotation='00:00', encoding='utf-8')

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)


#            时间           开盘     收盘    最高     最低       成交量     成交额   最新价
# 0  2023-05-08 09:30:00  120.39  120.39  120.39  120.390      47    56583.0  120.3900
# 1  2023-05-08 09:31:00  120.35  119.67  120.35  119.551     926  1109913.0  119.8866

def back_test():
    # 获取可转债实时行情
    kzz_spot = ak.bond_zh_hs_cov_spot()
    kzz_spot['rise'] = kzz_spot.changepercent.astype('float')


    # 取涨幅前20
    kzz_sort = kzz_spot.sort_values(by="rise", ascending=False)
    kzz_top = kzz_sort[:10].copy()

    res = 0
    # 遍历筛选
    for index, row in kzz_top.iterrows():

        symbol = row["symbol"]
        kzz_min_df = ak.bond_zh_hs_cov_min(symbol=symbol, period='1', adjust='')
        income = back(kzz_min_df, row["settlement"], row["name"])
        res = res + income

    print(res)

def back(kzz_min_df, settlement, name):
    jc_index = 0
    bug_price = 0
    bug_index = 0
    for index, row in kzz_min_df.iterrows():
        high = row["最高"]
        # 买入策略 1.当前1分钟内最高价涨幅介于3-6之间 2.不是新债
        if (1.03 < high / float(settlement) < 1.06) and (not name.startswith("N")):
            bug_index = index
            bug_price = high
            break
    if bug_index == 0:
        return 0

    closes = kzz_min_df.收盘.values
    dif, dea, macd = MACD(closes, SHORT=12, LONG=26, M=9)
    for index in range(len(macd)):
        if macd[index] < 0 and bug_index + 20 < index:
            jc_index = index
            break

    sell_price = kzz_min_df.loc[jc_index, "最低"]
    income = (sell_price / bug_price - 1) * 100

    buy_time = kzz_min_df.loc[bug_index, "时间"]
    sell_time = kzz_min_df.loc[jc_index, "时间"]
    logger.info(f"通知：{name} 股票在 {buy_time} 以 {bug_price} 的价格买入，在 {sell_time} 以 {sell_price} 的价格卖出，盈利{income}")
    return income


if __name__ == '__main__':
    back_test()

# print(macd.dtype)
# plt.figure(figsize=(15,8))
# plt.plot(dif,label='dif')
# plt.plot(dea,label='dea')
# plt.plot(macd,label='macd')
# plt.show()
# print(macd)
# back_test()
