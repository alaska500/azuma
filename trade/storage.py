import os
import sqlite3
from datetime import datetime

now = datetime.now()
month_str = now.strftime("%Y-%m")
date_str = now.strftime("%Y_%m_%d")
today = now.strftime("%Y-%m-%d")
target_dir = f'../storage'
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

tabel_name = f"trade_{date_str}"

create_tabel_sql = f'''create table if not exists {tabel_name}
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


def dict_factory(cursor, row):
    # 将游标获取的数据处理成字典返回
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


connect = sqlite3.connect(f"{target_dir}/trade_{month_str}.db",
                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
connect.row_factory = dict_factory

cursor = connect.cursor()
cursor.execute(create_tabel_sql)
connect.commit()


def insert_buy_info(symbol, name, buy_price, buy_change, buy_time, yesterday_close):
    cursor.execute(f"insert into {tabel_name} (date,symbol,name,yesterday_close,buy_price,buy_change,buy_time) values(?,?,?,?,?,?,?)",
                   (today, symbol, name, yesterday_close, buy_price, buy_change, buy_time))
    connect.commit()


def insert_sell_info(symbol, income, sell_price, sell_change, sell_time):
    cursor.execute(
        f"update {tabel_name} set status = 2, income={income}, sell_price={sell_price}, sell_change={sell_change}, sell_time=? where id = (select id from {tabel_name} where symbol  = {symbol} and status = 1 order by id desc limit 1)",
        [sell_time])
    connect.commit()


def select_position_list():
    result = cursor.execute(f"select * from {tabel_name} where status =  1")
    return result.fetchall()


def is_bought(symbol):
    result = cursor.execute(f"select * from {tabel_name} where symbol=? and date = ? and status = 1", (symbol, today))
    return False if result.fetchone() is None else True


def select_buy_times(symbol):
    result = cursor.execute(f"select count(*) as ct from {tabel_name} where symbol=? and date = ?", (symbol, today))
    return result.fetchone()["ct"]


def is_sold(symbol):
    result = cursor.execute(f"select * from {tabel_name} where symbol=? and date = ? and status = 2", (symbol, today))
    return False if result.fetchone() is None else True


# 关闭
def close(self):
    # 先关闭游标再关闭数据库链接
    self.cursor.close()
    self.connect.close()


if __name__ == '__main__':
    select_buy_times("128091")
    kzz_position_list = select_position_list()
    kzz_position_dict_list = dict()
    print(kzz_position_list)
    for x in kzz_position_list:
        kzz_position_dict_list[x["symbol"]] = x

