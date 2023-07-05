import os
import sqlite3
import datetime
target_dir = f'../../storage'
now = datetime.datetime.now()
month_str = now.strftime("%Y-%m")

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

table_name = "sstrategy_20230615_3-16_0.5-0.5_2.5_280_top10"

index = table_name.find("_") + 1
start_date = f"{table_name[index:index+4]}-{table_name[index+4:index+6]}-{table_name[index+6:index+8]} 09:30:00"
start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

count = 0
while True:
    start_datetime = start_datetime + datetime.timedelta(seconds=1)
    ttt = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    result = cursor.execute(f'''select count(*) as ct from "{table_name}" where buy_time < ? and ? < sell_time''', (start_datetime, start_datetime))
    ct = result.fetchone()["ct"]
    if ct > count:
        count = ct
    print(start_datetime)
    if ttt.endswith("15:00:00"):
        break

print(f"count={count}")