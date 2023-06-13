import pandas as pd
import time as tm
import efinance as ef
import os
from util import stock_calendar
from loguru import logger
from datetime import datetime
import traceback
import back_model as bm


df = pd.read_csv("E:/script/2023-06-13_copy.csv", header=None)
df.columns = ["时间", '债券代码', '债券名称', '涨跌幅', '最新价', '最高', '最低', '今开', '成交量', '成交额', '昨日收盘']

start = 0
step = 50
while True:
    end = start + step
    dff = df[start:end].copy()
    start = end
    print("=====================================")
    print(dff.to_string())
    print("=====================================")
