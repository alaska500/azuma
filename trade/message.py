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


def send(text):
    lock.acquire()
    send_dingding_msg(text)
    time.sleep(2)
    lock.release()

def send_dingding_msg(text):

    timestamp = str(round(time.time() * 1000))
    secret = secret_key
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    proxy = {"http": None, "https": None}

    try:
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s" % (dd_token, timestamp, sign)
        json_text = to_msg(text)
        resp = requests.post(api_url,
                             json.dumps(json_text),
                             headers=headers,
                             timeout=15, proxies=proxy).text
        logger.info("发送钉钉消息成功,结果：" + resp)
    except Exception as e:
        logger.info("发送钉钉消息失败,错误：" + traceback.format_exc())

def to_msg(text):
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





if __name__ == '__main__':
    send("test")
