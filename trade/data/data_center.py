import akshare as ak
import os
from datetime import datetime


def download_kzz_min():
    # 获取可转债实时行情
    kzz_spot = ak.bond_zh_hs_cov_spot()
    kzz_spot['rise'] = kzz_spot.changepercent.astype('float')

    # 取涨幅前20
    kzz_spot_sort = kzz_spot.sort_values(by="rise", ascending=False)
    kzz_spot_top = kzz_spot_sort[:2].copy()

    date_str = datetime.now().strftime("%Y-%m-%d")
    dir = f"../../data/{date_str}/min"
    if not os.path.exists(dir):
        os.makedirs(dir)

    kzz_spot_top.to_csv(f"../../data/{date_str}/kzz_spot_top.csv")

    # 遍历
    for index, row in kzz_spot_top.iterrows():
        kzz_min_df = ak.bond_zh_hs_cov_min(symbol=row["symbol"], period='1', adjust='')
        kzz_min_df.to_csv(f"../../data/{date_str}]/min/{row['symbol']}.csv")


if __name__ == '__main__':
    download_kzz_min()
