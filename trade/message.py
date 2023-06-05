import datetime
import threading
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import traceback
from util import log_util

logger = log_util.get_logger()
dd_token = '1b692186495fed1ed460592f3412c5601bf1bc056d74cc9494b66c99fe04ef99'
secret_key = "SEC46e3c984343932b103a0b9ef0f5f3fc0e6315eb81e90f9a44bfa2daf4784cbd9"
lock = threading.Lock()


def generate_sign(timestamp):
    secret_enc = secret_key.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret_key)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    return urllib.parse.quote_plus(base64.b64encode(hmac_code))


def send_msg(body):
    timestamp = str(round(time.time() * 1000))
    sign = generate_sign(timestamp)
    proxy = {"http": None, "https": None}

    try:
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s" % (dd_token, timestamp, sign)
        resp = requests.post(api_url, json.dumps(body), headers=headers, timeout=15, proxies=proxy).text
        # logger.info("发送钉钉消息成功,结果：" + resp)
    except Exception as e:
        logger.info("发送钉钉消息失败,错误：" + traceback.format_exc())


def to_text_msg(text):
    json_text = {
        "msgtype": "text",
        "at": {
            "atMobiles": [],
            "isAtAll": False
        },
        "text": {
            "content": text
        }
    }
    return json_text


def send_text_msg(text):
    send_msg(to_text_msg(text))


def to_action_card_msg(msg, link):
    json_body = {
        "actionCard": {
            "title": msg,
            "text": msg,
            "btnOrientation": "0",
            "singleTitle": "阅读全文",
            "singleURL": link
        },
        "msgtype": "actionCard"
    }
    return json_body


def send_action_card_msg(msg, link):
    send_msg(to_action_card_msg(msg, link))


def send(text):
    lock.acquire()
    send_text_msg(text)
    time.sleep(2)
    lock.release()


if __name__ == '__main__':
    now = datetime.datetime.now()
    name = "光力转债"
    symbol = "123197"
    latest_price = "157.147"
    change = "3.45"
    buy_change = "4.35"
    type = "sell"

    if 'buy'.__eq__(type):
        msg = "操作:【😊】买入 \n时间:%s \n名称:%s \n代码:%s \n价格:%s \n买入涨幅:%s" % (now,  name, symbol, latest_price, change)
    else:
        msg = "操作:【😂】卖出 \n时间:%s \n名称:%s \n代码:%s \n价格:%s \n买入涨幅:%s \n卖出涨幅:%s" % (now,  name, symbol, latest_price, buy_change, change)

    send(msg)
