import chinese_calendar
import datetime


def get_tradeday(start_str, end_str):
    start = datetime.datetime.strptime(start_str, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_str, '%Y-%m-%d')
    # 获取指定范围内工作日列表
    lst = chinese_calendar.get_workdays(start, end)
    expt = []
    # 找出列表中的周六，周日，并添加到空列表
    for time in lst:
        if time.isoweekday() == 6 or time.isoweekday() == 7:
            expt.append(time)
    # 将周六周日排除出交易日列表
    for time in expt:
        lst.remove(time)
    date_list = [item.strftime('%Y%m%d') for item in lst]  # 列表生成式，strftime为转换日期格式
    return date_list


if __name__ == '__main__':
    _today = datetime.datetime(year=2023, month=6, day=22)
    print(chinese_calendar.is_workday(_today) and _today.isoweekday() < 6)
