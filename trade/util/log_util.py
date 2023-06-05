import os
from loguru import logger
from datetime import datetime

cur_path = os.path.abspath(os.path.dirname(__file__))   # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('trade')]   # 获取根目录

date = datetime.now().strftime("%Y-%m-%d")
logger.add(proj_path + '\\logs\\api_%s.log' % date, rotation='00:00', encoding='utf-8')

def get_logger():
    return logger
