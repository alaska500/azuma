import pandas as pd
import time as tm
import efinance as ef
import os
from util import stock_calendar
from loguru import logger
from datetime import datetime
import traceback
import back_model as bm
from util import MyTT


file_name = f"E:/script/min/20230613/min/110052.csv"
if not os.path.exists(file_name):
    print("11111")

ss = pd.read_csv(file_name, header=0, index_col=0)
print(ss)

df = pd.DataFrame()
if df:
    print("11111")

print(os.getlogin())
quote_history = ef.bond.get_quote_history("123067", beg="20230616", end="20230616", klt=1)
quote_list = pd.DataFrame()
quote_list["收盘"] = quote_history.loc[quote_history['日期'] < "2023-06-16 10:21"]["收盘"][:1]
print(quote_list.to_string())
quote_list.loc[len(quote_list.index)] = 160.600
quote_list['DIF'], quote_list['DEA'], quote_list['MACD'] = MyTT.MACD(quote_list["收盘"])
print(quote_list[-5:].to_string())
print(quote_list.iloc[len(quote_list.index) - 1, 3])
