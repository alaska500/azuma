import efinance as ef
from loguru import logger
import pandas as pd
import traceback
import os
from datetime import datetime

# logger
logger.add('../../logs/data_{time}.log', rotation='00:00')


pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 设置打印宽度(**重要**)
pd.set_option('display.width', None)


def download_kzz_min():
    try:
        # 获取可转债实时行情
        kzz_spot = ef.bond.get_realtime_quotes()
        # 数据中的-替换成-100
        kzz_spot["涨跌幅"].replace(r'-', "-100", inplace=True)
        # 将列类型转换成float便于排序
        kzz_spot['涨跌幅'] = kzz_spot['涨跌幅'].astype(float)
        # 按涨跌幅排序
        kzz_sort = kzz_spot.sort_values(by="涨跌幅", ascending=False)
        # 取出前20
        kzz_top = kzz_sort[:50].copy()
        #重新设置下标
        kzz_top.index = range(len(kzz_top))

        date_str = datetime.now().strftime("%Y-%m-%d")
        dir = f"E:/kzz/data/{date_str}/min"
        if not os.path.exists(dir):
            os.makedirs(dir)

        kzz_top.to_csv(f"E:/kzz/data/{date_str}/kzz_spot_top.csv")

        # 遍历
        for row in kzz_top.itertuples():
            symbol = getattr(row, "债券代码")
            close = float(getattr(row, "昨日收盘"))
            kzz_min_df = ef.stock.get_quote_history(symbol, klt=1)
            for index, row in kzz_min_df.iterrows():
                change = (float(row['最低']) / close - 1) * 100
                kzz_min_df.loc[index, "涨幅"] = round(change, 5)

            kzz_min_df.to_csv(f"E:/kzz/data/{date_str}/min/{symbol}.csv")

    except Exception:
        logger.error(traceback.format_exc())

def data_handler(date_str):
    kzz_spot_top_file_name = f"E:/kzz/data/{date_str}/kzz_spot_top.csv"
    kzz_spot_top = pd.read_csv(kzz_spot_top_file_name)

    # 分钟涨幅榜单 列为1分钟tick 行数据为kzz代码 按涨幅排序
    change_rank = pd.DataFrame()

    kzz_min_df_list = list()
    for row in kzz_spot_top.itertuples():
        symbol = getattr(row, "债券代码")
        file_name = f"E:/kzz/data/{date_str}/min/{symbol}.csv"
        kzz_min_df = pd.read_csv(file_name)
        kzz_min_df_list.append(kzz_min_df)

    for time_index in range (240):
        one_min_change_df = pd.DataFrame(columns=['日期', '股票代码', '涨幅'])
        for index in range(len(kzz_min_df_list)):
            kzz_min_df = kzz_min_df_list[index]
            row = kzz_min_df.loc[time_index]
            date = row['日期']
            sybmol = row['股票代码']
            change = row['涨幅']
            one_min_change_df.loc[index] = [date, sybmol, change]
        one_min_change_df['涨幅'] = one_min_change_df.涨幅.astype('float')
        one_min_change_sort_df = one_min_change_df.sort_values(by="涨幅", ascending=False)
        one_min_change_sort_df.index = range(len(one_min_change_sort_df))
        #change_rank[time_index+1] = one_min_change_sort_df["股票代码"]
        change_rank.insert(time_index, time_index+1, one_min_change_sort_df["股票代码"])

    change_rank.to_csv(f"E:/kzz/data/{date_str}/kzz_change_top_rank.csv")



if __name__ == '__main__':
    download_kzz_min()
    data_handler(datetime.now().strftime("%Y-%m-%d"))