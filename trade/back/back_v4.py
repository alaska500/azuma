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
logger.add('..\\..\\alogs\\iinfo_%s.log' % today, filter=lambda record: record["level"].name == "INFO", rotation='00:00', encoding='utf-8')
logger.add("..\\..\\alogs\\debug_%s.log" % today, filter=lambda record: record["level"].name == "DEBUG", rotation='00:00', encoding='utf-8')

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


def backup_v3(date, symbol, quote, kzz_tick, strategy):
    position = bm.TradePosition()
    position.symbol = symbol
    position.date = date
    position.name = quote.loc[0, '债券名称']

    close = quote.loc[0, '收盘']
    change = quote.loc[0, '涨跌幅']
    open_price = quote.loc[0, '开盘']
    yesterday_close = round(close / (1 + change * 0.01), 6)
    # 如果开盘价大于7% 取消买入
    if (open_price / yesterday_close - 1) > 0.07:
        return position

    high_temp = open_price
    buy_flag = False
    for row in kzz_tick.itertuples():
        time = getattr(row, '时间')

        price = getattr(row, '成交价')
        change = round((price / yesterday_close) - 1, 6)

        high_temp = price if price > high_temp else high_temp
        high_change_temp = round((high_temp / yesterday_close) - 1, 6)

        if time < '09:30:20':
            continue

        if not buy_flag and (change > strategy.buy_change) and (change >= high_change_temp):
            position.set_buy_info(price, change, time)
            buy_flag = True
            continue
        if buy_flag and (change < high_change_temp - 0.005):
            position.set_sell_info(price, change, time)
            break
        if buy_flag and (change < strategy.stop_loss):
            position.set_sell_info(price, change, time)
            break

    if buy_flag and position.sell_price is None:
        position.set_sell_info(position.buy_price, position.buy_change, "00:00:00")

    if buy_flag and position.buy_price:
        position.income = round((position.sell_change - position.buy_change) * 100, 6)

    return position


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
            kzz_tick = get_kzz_tick_data(file_name)

            for strategy in strategy_list:
                position = backup_v3(trade_date, symbol, quote, kzz_tick, strategy)
                if position.buy_price:
                    new_row = [position.date, position.symbol, position.name, position.buy_price, position.buy_change,
                               position.buy_time, position.sell_price, position.sell_change, position.sell_time, position.income]
                    strategy.result_df.loc[len(strategy.result_df)] = new_row
                    # logger.debug("%s %s %s %s\t\t%s\t\t\t%s\t\t%s\t\t\t%s\t\t%s\t\t%s" % (
                    # position.date, position.symbol, position.name, position.buy_price, position.buy_change,
                    # position.buy_time,position.sell_price, position.sell_change, position.sell_time, position.income))
                    # logger.debug(f"{symbol} {date} 策略{strategy.name} 收益{position.income}")
                    if position.income > 0:
                        strategy.red = strategy.red + 1
                    else:
                        strategy.green = strategy.green + 1
                    strategy.income = strategy.income + position.income
            # logger.debug(f"{symbol} {trade_date}回测完成")
        # logger.debug(f"{symbol} 回测完成")


    for strategy in strategy_list:
        if strategy.result_df.empty:
            continue
        back_result_sort_df = strategy.result_df.sort_values(by=["日期", "买入时间"], ascending=[True, True])
        back_result_sort_df.index = range(len(back_result_sort_df))
        back_result_sort_df.to_csv(f"..\\..\\bresult\\{strategy.name}.csv")

        for trade_date in trade_date_list:
            back_result = back_result_sort_df.loc[back_result_sort_df['日期'] == trade_date]
            daily_income = 0
            if not back_result.empty:
                daily_income = back_result["收益"].sum()
            logger.info(f"日期:{trade_date} 策略:{strategy.name} 收益:{daily_income}")

        logger.info(f"over 策略:{strategy.name} 当月总收益:{round(strategy.income,8)} 红{strategy.red}次 绿{strategy.green}次")


    for strategy in strategy_list:
        logger.info(f"over 策略:{strategy.name} 当月总收益:{round(strategy.income,8)} 红{strategy.red}次 绿{strategy.green}次")


if __name__ == '__main__':
    trade_date_list = stock_calendar.get_tradeday('2023-04-01', '2023-04-30')
    kzz_symbol_list = get_kzz_all_base_info()

    strategy_list = list()
    strategy_list.append(bm.TradeStrategy(0.02, 0.025, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.030, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.035, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.040, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.045, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.050, 0.016))
    strategy_list.append(bm.TradeStrategy(0.02, 0.055, 0.016))

    strategy_list.append(bm.TradeStrategy(0.025, 0.030, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.035, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.040, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.045, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.050, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.055, 0.021))
    strategy_list.append(bm.TradeStrategy(0.025, 0.060, 0.021))

    strategy_list.append(bm.TradeStrategy(0.030, 0.035, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.040, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.045, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.050, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.055, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.060, 0.026))
    strategy_list.append(bm.TradeStrategy(0.030, 0.065, 0.026))

    strategy_list.append(bm.TradeStrategy(0.035, 0.040, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.045, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.050, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.055, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.060, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.065, 0.031))
    strategy_list.append(bm.TradeStrategy(0.035, 0.070, 0.031))

    strategy_list.append(bm.TradeStrategy(0.040, 0.045, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.050, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.055, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.060, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.065, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.070, 0.036))
    strategy_list.append(bm.TradeStrategy(0.040, 0.075, 0.036))

    strategy_list.append(bm.TradeStrategy(0.045, 0.050, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.055, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.060, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.065, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.070, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.075, 0.041))
    strategy_list.append(bm.TradeStrategy(0.045, 0.080, 0.041))

    strategy_list.append(bm.TradeStrategy(0.050, 0.055, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.060, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.065, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.070, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.075, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.080, 0.046))
    strategy_list.append(bm.TradeStrategy(0.050, 0.085, 0.046))

    strategy_list.append(bm.TradeStrategy(0.055, 0.060, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.065, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.070, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.075, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.080, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.085, 0.051))
    strategy_list.append(bm.TradeStrategy(0.055, 0.090, 0.051))

    list_b = [bm.TradeStrategy(0.020, 0.030, 0.015), bm.TradeStrategy(0.025, 0.035, 0.020),
              bm.TradeStrategy(0.030, 0.040, 0.025), bm.TradeStrategy(0.035, 0.045, 0.030),
              bm.TradeStrategy(0.040, 0.050, 0.035), bm.TradeStrategy(0.045, 0.055, 0.040),
              bm.TradeStrategy(0.050, 0.060, 0.045), bm.TradeStrategy(0.055, 0.065, 0.050)]


    hanle_strategy_v3(trade_date_list, kzz_symbol_list, list_b)
    #hanle_strategy_v3(trade_date_list, kzz_symbol_list, strategy_list)
