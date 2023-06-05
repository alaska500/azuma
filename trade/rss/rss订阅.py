import time
import requests
import xml.etree.cElementTree as ET
from datetime import datetime
from message import send_action_card_msg

# 26115886  冲击回本之路         https://space.bilibili.com/26115886
# 34941880  Unstoppable复盘     https://space.bilibili.com/34941880
# 527478198 一个月只做一只股      https://space.bilibili.com/527478198
# 20423082  惜取此时心           https://space.bilibili.com/20423082
# 439179909 玄学炒股越炒越悬      https://space.bilibili.com/439179909
# 625315686 目标1000万的股桃     https://space.bilibili.com/625315686
# 277358563 喜欢玩股票的关注我    https://space.bilibili.com/277358563
# 340033480 博约心缠            https://space.bilibili.com/340033480
# 27256828  緣筱梦              https://space.bilibili.com/27256828
# 106522687 胡胡是大长腿         https://space.bilibili.com/106522687
# 527688868 凛冬已尽            https://space.bilibili.com/527688868
# 322005137 史诗级韭菜           https://space.bilibili.com/322005137
# 43295527  AxeHedgeFund       https://space.bilibili.com/43295527
# 8660198   罗广文              https://space.bilibili.com/8660198
# 36711012  炒短养家             https://space.bilibili.com/36711012
# 396327539 财经阳同学           https://space.bilibili.com/396327539
# 689181375 长路量价             https://space.bilibili.com/689181375

#bilibili_uid_list = [26115886, 34941880, 527478198, 20423082, 439179909, 625315686, 277358563, 340033480, 27256828,
#                     106522687, 527688868, 322005137, 43295527, 8660198, 36711012, 396327539, 689181375]
bilibili_uid_list = [98446088]
bilibili_user_dynamic_url = 'https://rsshub.moeyy.cn/bilibili/user/dynamic/'
bilibili_user_video_url = 'https://rsshub.moeyy.cn/bilibili/user/video/'
bilibili_rss_url_list = [bilibili_user_video_url, bilibili_user_dynamic_url]


def get_rss_hub(url):
    proxy = {"http": None, "https": None}
    res = requests.get(url, proxies=proxy)
    if res.status_code == 200:
        return res.text
    else:
        return None


def rss():
    for uid in bilibili_uid_list:
        for url in bilibili_rss_url_list:
            time.sleep(0.7)
            res = get_rss_hub(url + str(uid))
            if res is None:
                continue

            print(uid)
            root = ET.fromstring(res)
            channel_title = root[0].find("title").text

            for item in root.iter('item'):
                title = item.find("title").text
                description = item.find("description").text
                pubDate = item.find("pubDate").text
                link = item.find("link").text

                pub_time = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S GMT')
                if (datetime.now() - pub_time).total_seconds() < 30 + 8*60*60:
                    msg = "### %s \n > %s" % (channel_title, title)
                    send_action_card_msg(msg, link)
                else:
                    break


if __name__ == '__main__':

    while True:
        rss()
        time.sleep(30)
