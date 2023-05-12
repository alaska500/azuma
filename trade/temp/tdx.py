import os
import pandas as pd
from struct import unpack

proj_path = os.path.dirname(__file__)    # 数据提取脚本地址

def extact_data(source_dir,file_name):
    # 通达信5分钟线*.lc5文件和*.lc1文件
    #     文件名即股票代码
    #     每32个字节为一个5分钟数据，每字段内低字节在前
    #     00 ~ 01 字节：日期，整型，设其值为num，则日期计算方法为：
    #                   year=floor(num/2048)+2004;
    #                   month=floor(mod(num,2048)/100);
    #                   day=mod(mod(num,2048),100);
    #     02 ~ 03 字节： 从0点开始至目前的分钟数，整型
    #     04 ~ 07 字节：开盘价，float型
    #     08 ~ 11 字节：最高价，float型
    #     12 ~ 15 字节：最低价，float型
    #     16 ~ 19 字节：收盘价，float型
    #     20 ~ 23 字节：成交额，float型
    #     24 ~ 27 字节：成交量（股），整型
    #     28 ~ 31 字节：（保留）

    # 以二进制方式打开源文件
    ofile = open(source_dir + os.sep + file_name, 'rb')
    buf = ofile.read()
    ofile.close()

    num = len(buf)
    no = num // 32
    # 原来是这样的，在python2中， '整数 / 整数 = 整数'，以上面的 100 / 2 就会等于 50， 并且是整数。
    # 而在python3中， ‘整数/整数 = 浮点数’， 也就是100 / 2 = 50.0， 不过，使用 '//'就可以达到原python2中'/'的效果。

    b = 0
    e = 32
    dl = []
    for i in range(no):
        # 将字节流转换成Python数据格式
        # I: unsigned int
        # f: float
        a = unpack('hhfffffii', buf[b:e])
        dl.append([str(int(a[0] / 2048) + 2035) + '-' + str(int(a[0] % 2048 / 100)).zfill(2) + '-' + str(
            a[0] % 2048 % 100).zfill(2), str(int(a[1] / 60)).zfill(2) + ':' + str(a[1] % 60).zfill(2) + ':00', a[2], a[3],
                   a[4], a[5], a[6], a[7]])
        b = b + 32
        e = e + 32
    df = pd.DataFrame(dl, columns=['date', 'time', 'open', 'high', 'low', 'close', 'amount', 'volume'])
    return df


def transform_data():
    # 保存csv文件的目录
    target = proj_path + '/data/tdxqh/time'
    if not os.path.exists(target):
        os.makedirs(target)
    code_list = []
    # 5分钟数据地址C:/qh/tdx/vipdoc/ds/fzline ；1分种数据地址C:/qh/tdx/vipdoc/ds/minline
    source_list = ['D:/new_tdx/vipdoc/ds/minline']

    for source in source_list:
        if source =='D:/new_tdx/vipdoc/ds/fzline':
            file_list = os.listdir(source)
            # 逐个文件进行解析
            for f in file_list:
                index1=f.rfind(".")
                index2=f.rfind('#')
                new_name1 ='minutes5-'+f[index2 + 1:index1]+'.csv'
                df = extact_data(source,f)
                df.date = df.date + " " + df.time
                da=pd.DataFrame(df, columns=['date','open','high','low','close','volume'])
                da.to_csv(target+os.sep+new_name1)
        else:
            file_list = os.listdir(source)
            # 逐个文件进行解析
            for f in file_list:
                index1 = f.rfind(".")
                index2 = f.rfind('#')
                new_name2 ='minutes1-' + f[index2 + 1:index1] + '.csv'
                df = extact_data(source, f)
                df.date = df.date + " " + df.time
                da = pd.DataFrame(df, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                da.to_csv(target + os.sep + new_name2)
# 获取所有股票/指数代码
# code_list.extend(list(map(lambda x: x[:x.rindex('.')], file_list)))
# 保存所有代码列表
# pd.DataFrame(data=code_list, columns=['code']).to_csv(proj_path + 'data/tdx/all_codes.csv', index=False)
if __name__ == "__main__":
    transform_data()