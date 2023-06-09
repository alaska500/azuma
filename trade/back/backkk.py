import pandas as pd
import efinance as ef
import os
from util import stock_calendar
from loguru import logger
from datetime import datetime
import traceback

date = datetime.now().strftime("%Y-%m-%d")
logger.add('..\\..\\alogs\\api_%s.log' % date, rotation='00:00', encoding='utf-8')


class TradeStrategy:
    def __init__(self, name, buy_change, stop_profit, stop_loss):
        self.name = name
        self.buy_change = buy_change
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
        self.income = 0.0
        self.red = 0
        self.green = 0
        self.result_df = pd.DataFrame(
            columns=['日期', '债券代码', "债券名称", '买入价格', '买入涨幅', '买入时间', '卖出价格', '卖出涨幅',
                     '卖出时间', '收益'])


class TradePosition:
    def __init__(self):
        self.date = None
        self.symbol = None
        self.name = None
        self.buy_price = None
        self.buy_change = None
        self.buy_time = None
        self.sell_price = None
        self.sell_change = None
        self.sell_time = None
        self.income = None

    def set_sell_info(self, sell_price, sell_change, sell_time):
        self.sell_price = sell_price
        self.sell_change = sell_change
        self.sell_time = sell_time

    def set_buy_info(self, buy_price, buy_change, buy_time):
        self.buy_price = buy_price
        self.buy_change = buy_change
        self.buy_time = buy_time


def get_kzz_all_base_info():
    kzz_all_base_info = ef.bond.get_all_base_info()
    return kzz_all_base_info["债券代码"].tolist()


def backup(date, symbol, file_name, strategy):
    position = TradePosition()
    position.symbol = symbol
    position.date = date

    kzz_tick = pd.read_csv(file_name, encoding='gb2312')
    quote = ef.bond.get_quote_history(str(symbol), beg=date, end=date)
    if quote.empty:
        return position
    position.name = quote.loc[0, '债券名称']

    close = quote.loc[0, '收盘']
    change = quote.loc[0, '涨跌幅']
    yesterday_close = round(close / (1 + change * 0.01), 6)

    buy_flag = False
    for row in kzz_tick.itertuples():
        time = getattr(row, '时间')
        if time < '09:30:20':
            continue

        price = getattr(row, '成交价')
        change = round((price / yesterday_close) - 1, 6)
        if not buy_flag and (change > strategy.buy_change):
            position.set_buy_info(price, change, time)
            buy_flag = True
            continue
        if buy_flag and ((price / yesterday_close) - 1 > strategy.stop_profit):
            position.set_sell_info(price, change, time)
            break
        if buy_flag and ((price / yesterday_close) - 1 < strategy.stop_loss):
            position.set_sell_info(price, change, time)
            break

    if position.sell_price is None:
        position.set_sell_info(position.buy_price, position.buy_change, "00:00:00")

    if position.buy_price:
        position.income = round(position.sell_change - position.buy_change, 6) * 100

    return position


def hanle_strategy(trade_date_list, kzz_symbol_list, strategy):
    for date in trade_date_list:
        total_income_daily = 0

        for symbol in kzz_symbol_list:

            file_name = f"E:/202304SH股票五档分笔/{date}/{symbol}_{date}.csv"
            if not os.path.exists(file_name):
                continue

            position = backup(date, symbol, file_name, strategy)
            if position.buy_price:
                new_row = [position.date, position.symbol, position.name, position.buy_price, position.buy_change,
                           position.buy_time, position.sell_price, position.sell_change, position.sell_time,
                           position.income]
                strategy.result_df.loc[len(strategy.result_df)] = new_row
                # logger.info("%s %s %s %s\t\t%s\t\t\t%s\t\t%s\t\t\t%s\t\t%s\t\t%s" % (
                # position.date, position.symbol, position.name, position.buy_price, position.buy_change,
                # position.buy_time,position.sell_price, position.sell_change, position.sell_time, position.income))
                if position.income > 0:
                    strategy.red = strategy.red + 1
                else:
                    strategy.green = strategy.green + 1
                total_income_daily = total_income_daily + position.income

        logger.info(f"日期：{date} 收益为：{total_income_daily}")
        strategy.income = strategy.income + total_income_daily

    strategy.result_df.to_csv(f"..\\..\\aresult\\{strategy.name}.csv")
    logger.info(f"：这个月的总收益为：{strategy.income} 红{strategy.red}次 绿{strategy.green}次")


if __name__ == '__main__':

    trade_date_list = stock_calendar.get_tradeday('2023-04-01', '2023-04-30')
    kzz_symbol_list = get_kzz_all_base_info()

    strategy1 = TradeStrategy("strategy1", 0.03, 0.050, 0.026)
    strategy2 = TradeStrategy("strategy2", 0.03, 0.045, 0.026)
    strategy3 = TradeStrategy("strategy3", 0.03, 0.040, 0.026)
    strategy4 = TradeStrategy("strategy4", 0.03, 0.035, 0.026)

    strategy_list = [strategy1, strategy2, strategy3, strategy4]

    for strategy in strategy_list:
        logger.info(
            f"策略{strategy.name}开始。 买入:{strategy.buy_change}  止盈:{strategy.stop_profit}  止损:{strategy.stop_loss}")
        hanle_strategy(trade_date_list, kzz_symbol_list, strategy)
        logger.info(f"策略{strategy.name}结束。 收益:{strategy.income}")
