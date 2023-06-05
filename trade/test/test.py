import efinance as ef
from loguru import logger
import pandas as pd
import time
from datetime import datetime

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

while True:
    date = datetime.now().strftime("%Y%m%d")
    df = ef.bond.get_quote_history('118021', beg=date)[-1:]
    print(df)
    name = df.loc[0, '债券名称']
    latest_price = df.loc[0, '收盘']
    high = df.loc[0, '最高']
    change = df.loc[0, '涨跌幅']
    print(f"{name}  {latest_price} {high} {change}")
    time.sleep(0.5)


# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8', filter=lambda record: record["level"].name == "INFO")




# 股票代码
stock_code = '123130'
# 5 分钟
frequency = 1
df = ef.stock.get_quote_history(stock_code, klt=frequency)
print(df[:20])