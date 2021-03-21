# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 00:59

import requests
import json
import time
from config import global_config
from logger import logger
from push import push

DYNAMIC_DICT = {}


def query_dynamic(uid=None):
    if uid is None:
        return
    uid = str(uid)
    query_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history' \
                '?host_uid={uid}&offset_dynamic_id=0&need_top=0&platform=web'.format(uid=uid)
    response = requests.get(query_url)
    if response.status_code == 200:
        result = json.loads(str(response.content, 'utf-8'))
        if result['code'] == 0:
            data = result['data']
            if len(data['cards']) == 0:
                logger.info('【查询】【{uid}】动态列表为空'.format(uid=uid))
                return

            item = data['cards'][0]
            dynamic_id = item['desc']['dynamic_id']
            uname = item['desc']['user_profile']['info']['uname']

            if DYNAMIC_DICT.get(uid, None) is None:
                DYNAMIC_DICT[uid] = dynamic_id
                logger.info('【查询】【{uname}】动态初始化'.format(uname=uname))
                return

            if DYNAMIC_DICT.get(uid, None) != dynamic_id:
                DYNAMIC_DICT[uid] = dynamic_id

                dynamic_type = item['desc']['type']
                if dynamic_type not in [1, 2, 4, 8, 64]:
                    logger.info('【查询】【{uname}】动态有更新，但不在需要推送的动态类型列表中'.format(uname=uname))
                    return

                timestamp = item['desc']['timestamp']
                dynamic_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                card_str = item['card']
                card = json.loads(card_str)

                content = None
                pic_url = None
                if dynamic_type == 1:
                    # 转发动态
                    content = card['item']['content']
                elif dynamic_type == 2:
                    # 图文动态
                    content = card['item']['description']
                    pic_url = card['item']['pictures'][0]['img_src']
                elif dynamic_type == 4:
                    # 文字动态
                    content = card['item']['content']
                elif dynamic_type == 8:
                    # 投稿动态
                    content = card['item']['title']
                elif dynamic_type == 64:
                    # 专栏动态
                    content = card['title']
                    pic_url = card['image_urls'][0]
                logger.info('【查询】【{uname}】动态有更新，准备推送：{content}'.format(uname=uname, content=content[:30]))
                push.push_msg(uname, dynamic_id, content, pic_url, dynamic_type, dynamic_time)
        else:
            logger.error('【查询】请求返回数据code错误：{code}'.format(code=result['code']))


if __name__ == '__main__':
    intervals_second = global_config.get_raw('config', 'intervals_second')
    intervals_second = int(intervals_second)
    uid_list = global_config.get_raw('config', 'uid_list').split(',')
    begin_time = global_config.get_raw('config', 'begin_time')
    end_time = global_config.get_raw('config', 'end_time')

    if begin_time == '':
        begin_time = '00:00'
    if end_time == '':
        end_time = '23:59'

    logger.info('开始检测')
    while True:
        current_time = time.strftime("%H:%M", time.localtime(time.time()))
        if begin_time <= current_time <= end_time:
            for _ in uid_list:
                query_dynamic(_)
        time.sleep(intervals_second)
