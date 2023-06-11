import pandas as pd
import time as tm
import efinance as ef
import os
from util import stock_calendar
from loguru import logger
from datetime import datetime
import traceback
import back_model as bm

today = datetime.now().strftime("%Y-%m-%d")
logger.add("..\\..\\alogs\\info.log", filter=lambda record: record["level"].name == "INFO")
logger.add("..\\..\\alogs\\error.log", filter=lambda record: record["level"].name == "ERROR")
logger.add("..\\..\\alogs\\warning.log", filter=lambda record: record["level"].name == "WARNING")
logger.add("..\\..\\alogs\\debug.log", filter=lambda record: record["message"].__contains__("debug"))


os.environ['NO_PROXY'] = '*'


logger.warning("WARNINGdebug")
logger.info("INFOPdebug")
logger.error("ERRORdebug")