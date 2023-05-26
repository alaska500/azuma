from loguru import logger

logger.add('../logs/api_{time}.log', rotation='00:00', encoding='utf-8')


def get_logger():
    return logger
