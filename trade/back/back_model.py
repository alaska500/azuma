import pandas as pd
from back_storage import BackStorage


class TradeStrategy:
    def __init__(self, buy_change, stop_profit, stop_loss):
        self.name = f"strategy_{str(round(buy_change * 1000))}_{str(round(stop_profit * 1000))}"
        self.buy_change = buy_change
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
        self.daily_income = 0.0
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
        self.income = 0

    def set_sell_info(self, sell_price, sell_change, sell_time):
        self.sell_price = sell_price
        self.sell_change = sell_change
        self.sell_time = sell_time

    def set_buy_info(self, buy_price, buy_change, buy_time):
        self.buy_price = buy_price
        self.buy_change = buy_change
        self.buy_time = buy_time


def generate_table_name(buy__change_floor, buy_change_upper, stop_profit, stop_loss,
                        stop_loss_lowest, wait_time, back_date):
    return f"strategy_{back_date}_{buy__change_floor}-{buy_change_upper}_{stop_profit}-{stop_loss}_{stop_loss_lowest}_{wait_time}"


class TradeStrategyV2:
    def __init__(self, buy__change_floor, buy_change_upper, stop_profit, stop_loss, stop_loss_lowest, wait_time,
                 back_date, back_yesterday):
        self.back_date = back_date
        self.back_yesterday = back_yesterday
        self.buy__change_floor = buy__change_floor
        self.buy_change_upper = buy_change_upper
        self.wait_time = wait_time
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
        self.stop_loss_lowest = stop_loss_lowest
        self.table_name = generate_table_name(buy__change_floor, buy_change_upper, stop_profit, stop_loss,
                                              stop_loss_lowest, wait_time, back_date)
        self.back_storage = BackStorage(self.table_name)
        self.income = 0
