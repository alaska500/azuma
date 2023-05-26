from datetime import datetime
import pandas as pd
import os

now = datetime.now()
date_str = now.strftime("%Y-%m-%d")
target_dir = f'../storage/{date_str}'

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

bought_file_name = target_dir + "/bought.csv"
sold_file_name = target_dir + "/sold.csv"
position_file_name = target_dir + "/position.csv"


class TradeStorage:
    def __init__(self):
        self.bought_set = self.init_stock_info_from_file(bought_file_name)
        self.sold_set = self.init_stock_info_from_file(sold_file_name)
        self.position = self.init_position_info_from_file()

    # 当天已经交易过的股票
    def save_bought_stock(self, symbol):
        self.bought_set.add(symbol)
        with open(bought_file_name, 'a', encoding='utf-8') as file:
            file.write(symbol + "\n")

    def save_sold_stock(self, symbol):
        self.sold_set.add(symbol)
        with open(sold_file_name, 'a', encoding='utf-8') as file:
            file.write(symbol + "\n")

    def init_stock_info_from_file(self, file_name):
        if not os.path.exists(file_name):
            return set()

        with open(file_name, "r") as file:
            return set(file.read().splitlines())

    def init_position_info_from_file(self):
        if not os.path.exists(position_file_name) or os.path.getsize(position_file_name) == 0:
            return pd.DataFrame(columns=['债券名称', '买入时间', '买入价格', '买入时涨幅', '卖出时间', '卖出价格', '卖出时涨幅', '收益'])

        return pd.read_csv(position_file_name, index_col=0, engine='python')

    def insert_bought_position(self, symbol, name, buy_time, buy_price, buy_change):
        self.save_bought_stock(symbol)

        self.position.loc[int(symbol)] = {'债券名称':name, '买入时间':buy_time, '买入价格':buy_price, '买入时涨幅':buy_change}
        self.position.to_csv(position_file_name)

    def insert_sold_position(self, symbol, sold_time, sold_price, sold_change):
        self.save_sold_stock(symbol)

        symbol_int = int(symbol)
        self.position.loc[symbol_int, '卖出时间'] = sold_time
        self.position.loc[symbol_int, '卖出价格'] = sold_price
        self.position.loc[symbol_int, '卖出时涨幅'] = sold_change

        self.position.to_csv(position_file_name)

    def get_position(self, symbol):
        return self.position.loc[int(symbol)]

if __name__ == '__main__':
    tm = TradeStorage()
    print(tm.bought_set)