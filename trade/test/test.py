import efinance as ef
from loguru import logger
import pandas as pd
import time
from datetime import datetime
import os
from util import MyTT
import matplotlib.pyplot as plt


pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)
os.environ['NO_PROXY'] = '*'

dw = pd.DataFrame()


df = ef.bond.get_quote_history('113016', beg="20230611", klt=1)
print(df[-10:])

dw['DIF'], dw['DEA'], dw['MACD'] = MyTT.MACD(df["收盘"])
dw['K'], dw['D'], dw['J'] = MyTT.KDJ(df["收盘"], df["最高"], df["最低"])

plt.figure(figsize=(40, 40))
dw[['DIF', 'DEA', 'MACD']].plot()
