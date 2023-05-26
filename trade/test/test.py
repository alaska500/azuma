import efinance as ef
from loguru import logger
import pandas as pd

# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8', filter=lambda record: record["level"].name == "INFO")


pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)

# 股票代码
stock_code = '123130'
# 5 分钟
frequency = 1
df = ef.stock.get_quote_history(stock_code, klt=frequency)
print(df[:20])