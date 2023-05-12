import efinance as ef
from loguru import logger
import pandas as pd
import traceback
import os
import MyTT
from datetime import datetime

# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8',
           filter=lambda record: record["level"].name == "INFO")

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

result_df = pd.DataFrame(columns=['债券名称', '债券代码', '买入时间', '买入价格', '买入时涨幅', '卖出时间', '卖出价格', '卖出时涨幅', '收益'])

def download_kzz_min(date_str):
    kzz_spot_top_df = pd.read_csv(f"E:/kzz/data/{date_str}/kzz_spot_top.csv")
    # 取涨幅前20
    kzz_spot_top = kzz_spot_top_df[:12].copy()

    res = 0
    # 遍历筛选
    for index, row in kzz_spot_top.iterrows():
        symbol = row["债券代码"]
        file_name = f"E:/kzz/data/{date_str}/min/{symbol}.csv"
        kzz_min_df = pd.read_csv(file_name)
        income = back(kzz_min_df, row["债券名称"], symbol, float(row["昨日收盘"]), row["今开"])
        res = res + income
    logger.info("总收益为：" + str(res))
    result_df.to_csv(f"../../res/res_{date_str}.csv")


def back(kzz_min_df, name, symbol, settlement, open):
    buy_price = -1
    buy_index = -1
    change = -99

    # 寻找买点
    for index, row in kzz_min_df.iterrows():
        high = row["最高"]
        # 买入策略 1.当前1分钟内最高价涨幅介于3-5之间  3.开盘涨幅不超过5  2.不是新债
        change = (high / settlement - 1) * 100
        openChange = (open / settlement - 1) * 100
        if (3 < change < 5) and openChange < 5 and (not name.startswith("N")):
            buy_index = index
            buy_price = high
            break
    # 没有找到买点 返回
    if buy_index == -1:
        return 0

    # 寻找卖点 macd死叉卖出 没有就15点卖出
    sicha_index = 239
    closes = kzz_min_df.收盘.values
    dif, dea, macd = MyTT.MACD(closes, SHORT=12, LONG=26, M=9)

    for idx in range(len(macd)):
        if buy_index + 40 < idx and macd[idx] < 0:
            sicha_index = idx
            break

    sell_price = kzz_min_df.loc[sicha_index, "最低"]
    sell_change = ((sell_price / float(settlement)) - 1) * 100
    #计算收益
    income = (sell_price / buy_price - 1) * 100

    buy_time = kzz_min_df.loc[buy_index, "日期"]
    sell_time = kzz_min_df.loc[sicha_index, "日期"]
    new = "通知：【{:^6}】【{}】 股票在 {} 以 {:<8}  【{:<6}】 的价格买入，在 {} 以 {:<6} 【{:<6}】 的价格卖出，盈利{}"\
        .format(name, symbol, buy_time, buy_price, round(change, 4), sell_time, sell_price, round(sell_change, 4), round(income, 6))

    result_df.loc[len(result_df)] = {'债券名称':name, '债券代码':symbol, '买入时间':buy_time, '买入价格':buy_price, '买入时涨幅':round(change, 4), '卖出时间':sell_time, '卖出价格':sell_price, '卖出时涨幅':round(sell_change, 4), '收益':round(income, 6)}
    logger.info(new)
    return income


def get_settlement(kzz_spot_top_df, symbol):
    for index, row in kzz_spot_top_df.iterrows():
        if (row['债券代码'].equals(symbol)):
            return float(row['昨日收盘'])
    return 0


if __name__ == '__main__':
    download_kzz_min("2023-05-10")

#download_kzz_min(datetime.now().strftime("%Y-%m-%d"))
