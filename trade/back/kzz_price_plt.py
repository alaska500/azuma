import pandas as pd
from util import MyTT


import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as ticker

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
print(df[:10])

qzzz = df[df["债券代码"] == 110044].copy()
qzzz.index = range(len(qzzz))
print(qzzz[-100:].to_string())
qzzz['DIF'], qzzz['DEA'], qzzz['MACD'] = MyTT.MACD(qzzz["最新价"])

plt.figure(figsize=(20, 20))


plt.plot(qzzz['MACD'][:240], label = 'macd')
plt.plot(qzzz['DIF'][:240])
plt.plot(qzzz['DEA'][:240])
plt.plot(qzzz['涨跌幅'][:240])

plt.savefig('C:/Users/ly/Desktop/savefig_example1.png')
plt.show()
