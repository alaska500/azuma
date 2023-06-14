import os
import sqlite3
from datetime import datetime

now = datetime.now()
month_str = now.strftime("%Y-%m")
date_str = now.strftime("%Y_%m_%d")
today = now.strftime("%Y-%m-%d")
target_dir = f'../../storage'
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

def dict_factory(cursor, row):
    # 将游标获取的数据处理成字典返回
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


connect = sqlite3.connect(f"{target_dir}/back_trade_{month_str}.db",
                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
connect.row_factory = dict_factory
cursor = connect.cursor()


class BackStorage:
    def __init__(self, table_name_temp):
        self.table_name = table_name_temp
        
        create_table_sql = f'''create table if not exists "{self.table_name}"
        (
            id          INTEGER       primary key autoincrement,
            date        varchar(20)   not null,
            symbol      varchar(20)   not null,
            name        varchar(20)   not null,
            yesterday_close        decimal(8, 4)   not null,
            status      TINYINT       default '1',
            income      decimal(8, 4) default NULL,
            buy_time    datetime      not null,
            buy_price   decimal(8, 4) not null,
            buy_change  decimal(8, 4) not null,
            sell_time   datetime      default NULL,
            sell_price  decimal(8, 4) default NULL,
            sell_change decimal(8, 4) default NULL
        );
        '''
        cursor.execute(create_table_sql)
        connect.commit()
                

    def insert_buy_info(self, symbol, name, buy_price, buy_change, buy_time, yesterday_close):
        cursor.execute(
            f"insert into '{self.table_name}' (date,symbol,name,yesterday_close,buy_price,buy_change,buy_time) values(?,?,?,?,?,?,?)",
            (today, symbol, name, yesterday_close, buy_price, buy_change, buy_time))
        connect.commit()

    def insert_sell_info(self, symbol, income, sell_price, sell_change, sell_time):
        cursor.execute(
            f"update '{self.table_name}' set status = 2, income={income}, sell_price={sell_price}, sell_change={sell_change}, sell_time=? where id = (select id from '{self.table_name}' where symbol  = {symbol} and status = 1 order by id desc limit 1)",
            [sell_time])
        connect.commit()

    def select_position_list(self):
        result = cursor.execute(f"select * from '{self.table_name}' where status =  1")
        return result.fetchall()

    def is_bought(self, symbol):
        result = cursor.execute(f"select * from '{self.table_name}' where symbol=? and date = ? and status = 1",
                                (symbol, today))
        return False if result.fetchone() is None else True

    def select_buy_times(self, symbol):
        result = cursor.execute(f"select count(*) as ct from '{self.table_name}' where symbol=? and date = ?", (symbol, today))
        return result.fetchone()["ct"]

    def is_sold(self, symbol):
        result = cursor.execute(f"select * from '{self.table_name}' where symbol=? and date = ? and status = 2",
                                (symbol, today))
        return False if result.fetchone() is None else True

    def select_income(self):
        result = cursor.execute(f"select sum(income) as ic from '{self.table_name}'")
        return result.fetchone()["ic"]

    # 关闭
    def close(self):
        # 先关闭游标再关闭数据库链接
        cursor.close()
        connect.close()


if __name__ == '__main__':
    bs = BackStorage("str_6.4")
    bs.select_position_list()