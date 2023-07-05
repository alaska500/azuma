import pandas as pd
import time as tm
import efinance as ef
import os
from util import stock_calendar
from loguru import logger
from datetime import datetime
import traceback
import back_model as bm

today = datetime.now().strftime("%Y-%m-%d")
logger.add('..\\..\\alogs\\iinfo_%s.log' % today, filter=lambda record: record["level"].name == "INFO",
           rotation='00:00', encoding='utf-8')
logger.add("..\\..\\alogs\\debug_%s.log" % today, filter=lambda record: record["level"].name == "DEBUG",
           rotation='00:00', encoding='utf-8')

os.environ['NO_PROXY'] = '*'


def get_kzz_all_base_info():
    kzz_all_base_info = ef.bond.get_all_base_info()
    return kzz_all_base_info["债券代码"].tolist()


def get_quote_history(symbol, beg_date, end_date):
    quote = pd.DataFrame()
    try:
        quote = ef.bond.get_quote_history(str(symbol), beg=beg_date, end=end_date)
    except Exception:
        logger.debug(traceback.format_exc())
        tm.sleep(1)
    return quote


def get_kzz_tick_data(file_name):
    return pd.read_csv(file_name, encoding='gb2312')


def format_date(trade_date):
    return f"{trade_date[0:4]}-{trade_date[4:6]}-{trade_date[6:8]}"


def hanle_strategy_v3(trade_date_list, kzz_symbol_list, strategy_list):
    # 遍历股票 根据日期、策略回测收益
    index = 0
    for symbol in kzz_symbol_list:
        index = index + 1
        logger.debug(f"开始回测第{index}支股票")

        quote_list = get_quote_history(symbol, "20230401", "20230430")
        if quote_list.empty:
            # logger.debug(f"可转债:{symbol} 报价缺失")
            continue

        for trade_date in trade_date_list:
            file_name = f"E:/202304SH股票五档分笔/{trade_date}/{symbol}_{trade_date}.csv"
            if not os.path.exists(file_name):
                # logger.debug(f"可转债:{symbol} 日期:{trade_date} csv文件缺失")
                continue

            quote = quote_list.loc[quote_list['日期'] == format_date(trade_date)]
            if quote.empty:
                logger.debug(f"可转债:{symbol} 日期:{trade_date} 查找报价失败")
                continue

            quote.index = range(len(quote))
            close = quote.loc[0, '收盘']
            close_change = quote.loc[0, '涨跌幅']
            yesterday_close = round(close / (1 + close_change * 0.01), 6)
            kzz_tick = get_kzz_tick_data(file_name)

            for sss in strategy_list:
                flag = False
                for row in kzz_tick.itertuples():
                    price = getattr(row, '成交价')
                    change = round(((price / yesterday_close) - 1) * 100, 6)
                    if not flag and sss.stop_loss < change < sss.stop_loss + 1:
                        sss.red = sss.red + 1
                        sss.green = sss.green + 1
                        flag = True
                        continue
                    if flag and change > sss.stop_profit:
                        sss.green = sss.green + 1
                        break

    for sss in strategy_list:
        logger.info(f"策略：{sss.stop_loss}-{sss.stop_profit}    red={sss.red}  green={sss.green}")


if __name__ == '__main__':
    trade_date_list = stock_calendar.get_tradeday('2023-04-01', '2023-04-30')
    kzz_symbol_list = get_kzz_all_base_info()

    strategy_list = list()

    strategy_list.append(bm.TradeStrategy(0.02, 20, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 8, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 7, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 6, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 5, 3))
    strategy_list.append(bm.TradeStrategy(0.02, 4, 3))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 8, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 7, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 6, 4))
    strategy_list.append(bm.TradeStrategy(0.02, 5, 4))


    strategy_list.append(bm.TradeStrategy(0.02, 20, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 8, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 7, 5))
    strategy_list.append(bm.TradeStrategy(0.02, 6, 5))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 8, 6))
    strategy_list.append(bm.TradeStrategy(0.02, 7, 6))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 7))
    strategy_list.append(bm.TradeStrategy(0.02, 8, 7))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 8))
    strategy_list.append(bm.TradeStrategy(0.02, 9, 8))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 9))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 9))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 9))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 9))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 9))
    strategy_list.append(bm.TradeStrategy(0.02, 10, 9))

    strategy_list.append(bm.TradeStrategy(0.02, 20, 10))
    strategy_list.append(bm.TradeStrategy(0.02, 18, 10))
    strategy_list.append(bm.TradeStrategy(0.02, 16, 10))
    strategy_list.append(bm.TradeStrategy(0.02, 14, 10))
    strategy_list.append(bm.TradeStrategy(0.02, 12, 10))

    #kzz_symbol_list = ["123181"]
    hanle_strategy_v3(trade_date_list, kzz_symbol_list, strategy_list)
