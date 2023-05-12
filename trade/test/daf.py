import efinance as ef
from loguru import logger
from threading import Thread
import pandas as pd


pd.set_option('display.width', None)
#pd.set_option('max_rows', None)
#pd.set_option('max_columns', None)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.unicode.east_asian_width', True)


ss = float(-6.79)

# logger
logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8', filter=lambda record: record["level"].name == "INFO")

# while True:
# 获取可转债实时行情
kzz_spot = ef.bond.get_realtime_quotes()
# 数据中的-替换成-100
kzz_spot["涨跌幅"].replace(r'-', "-100", inplace=True)
# 将列类型转换成float便于排序
kzz_spot['涨跌幅'] = kzz_spot['涨跌幅'].astype(float)
# 按涨跌幅排序
kzz_sort = kzz_spot.sort_values(by="涨跌幅", ascending=False)
# 取出前20
sss = kzz_sort[:20].copy()
#重新设置下标
sss.index = range(len(sss))
print(sss)
logger.info("\n" + sss.to_string())
logger.info(sss.dtypes)


# 债券代码       object
# 债券名称       object
# 涨跌幅        float64
# 最新价         object
# 最高           object
# 最低           object
# 今开           object
# 涨跌额         object
# 换手率        float64
# 量比           object
# 动态市盈率     object
# 成交量         object
# 成交额         object
# 昨日收盘      float64
# 总市值         object
# 流通市值        int64
# 行情ID         object
# 市场类型       object
# 更新时间       object
# 最新交易日     object
# dtype: object