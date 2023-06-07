import sqlite3
import os
from datetime import datetime

now = datetime.now()
month_str = now.strftime("%Y-%m")
date_str = now.strftime("%Y_%m_%d")
today = now.strftime("%Y-%m-%d")
target_dir = f'../db_trade'
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

tabel_name = f"trade_{date_str}"

create_tabel_sql = f''' CREATE TABLE if not exists {tabel_name}(
    id INTEGER PRIMARY KEY   AUTOINCREMENT,
    date varchar(20) NOT NULL ,
    symbol varchar(20) NOT NULL ,
    name varchar(20) NOT NULL ,
    status TINYINT DEFAULT '1' ,
    income decimal(8,4) DEFAULT NULL ,
    buy_time datetime NOT NULL ,
    buy_price decimal(8,4) NOT NULL ,
    buy_change decimal(8,4) NOT NULL ,
    sell_time datetime DEFAULT NULL ,
    sell_price decimal(8,4) DEFAULT NULL ,
    sell_change decimal(8,4) DEFAULT NULL
);'''
connect = sqlite3.connect(f"{target_dir}/trade_{month_str}.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = connect.cursor()
connect.commit()
cursor.execute(create_tabel_sql)


def insert_buy_info(symbol, name, buy_time, buy_price, buy_change):
    cursor.execute(f"insert into {tabel_name} (date,symbol,name,buy_price,buy_change,buy_time) values(?,?,?,?,?,?)",
                   (today, symbol, name, buy_price, buy_change, buy_time))
    connect.commit()


def insert_sell_info(symbol, income, sell_price, sell_change, sell_time):
    cursor.execute(f"update {tabel_name} set status = 2, income={income}, sell_price={sell_price}, sell_change={sell_change}, sell_time=? where id = (select id from trade_2023_06_08 where symbol  = {symbol} order by id desc limit 1)", [sell_time])
    connect.commit()


def select_buy_change(symbol):
    change = cursor.execute(f"select buy_change from {tabel_name} where symbol=? and date = ?", (symbol, today))
    if change is None:
        return 0
    else:
        return change.fetchone()[0]


# 关闭
def close(self):
    # 先关闭游标再关闭数据库链接
    self.cursor.close()
    self.connect.close()



