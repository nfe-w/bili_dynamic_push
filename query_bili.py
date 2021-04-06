# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 00:59

import json
import time
from collections import deque

import util
from logger import logger
from push import push

DYNAMIC_DICT = {}
LIVING_STATUS_DICT = {}
LEN_OF_DEQUE = 20


def query_dynamic(uid=None):
    if uid is None:
        return
    uid = str(uid)
    query_url = 'http://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history' \
                '?host_uid={uid}&offset_dynamic_id=0&need_top=0&platform=web&my_ts={my_ts}'.format(uid=uid, my_ts=int(time.time()))
    headers = get_headers(uid)
    response = util.requests_get(query_url, '查询动态状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        result = json.loads(str(response.content, 'utf-8'))
        if result['code'] != 0:
            logger.error('【查询动态状态】请求返回数据code错误：{code}'.format(code=result['code']))
        else:
            data = result['data']
            if len(data['cards']) == 0:
                logger.info('【查询动态状态】【{uid}】动态列表为空'.format(uid=uid))
                return

            item = data['cards'][0]
            dynamic_id = item['desc']['dynamic_id']
            uname = item['desc']['user_profile']['info']['uname']

            if DYNAMIC_DICT.get(uid, None) is None:
                DYNAMIC_DICT[uid] = deque(maxlen=LEN_OF_DEQUE)
                cards = data['cards']
                for index in range(LEN_OF_DEQUE):
                    if index < len(cards):
                        DYNAMIC_DICT[uid].appendleft(cards[index]['desc']['dynamic_id'])
                logger.info('【查询动态状态】【{uname}】动态初始化：{queue}'.format(uname=uname, queue=DYNAMIC_DICT[uid]))
                return

            if dynamic_id not in DYNAMIC_DICT[uid]:
                previous_dynamic_id = DYNAMIC_DICT[uid].pop()
                DYNAMIC_DICT[uid].append(previous_dynamic_id)
                logger.info('【查询动态状态】【{}】上一条动态id[{}]，本条动态id[{}]'.format(uname, previous_dynamic_id, dynamic_id))
                DYNAMIC_DICT[uid].append(dynamic_id)
                logger.info(DYNAMIC_DICT[uid])

                dynamic_type = item['desc']['type']
                if dynamic_type not in [2, 4, 8, 64]:
                    logger.info('【查询动态状态】【{uname}】动态有更新，但不在需要推送的动态类型列表中'.format(uname=uname))
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
                    content = card['title']
                    pic_url = card['pic']
                elif dynamic_type == 64:
                    # 专栏动态
                    content = card['title']
                    pic_url = card['image_urls'][0]
                logger.info('【查询动态状态】【{uname}】动态有更新，准备推送：{content}'.format(uname=uname, content=content[:30]))
                push.push_for_bili_dynamic(uname, dynamic_id, content, pic_url, dynamic_type, dynamic_time)


def query_live_status(uid=None):
    if uid is None:
        return
    uid = str(uid)
    query_url = 'http://api.bilibili.com/x/space/acc/info?mid={}&my_ts={}'.format(uid, int(time.time()))
    headers = get_headers(uid)
    response = util.requests_get(query_url, '查询直播状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        result = json.loads(str(response.content, 'utf-8'))
        if result['code'] != 0:
            logger.error('【查询直播状态】请求返回数据code错误：{code}'.format(code=result['code']))
        else:
            name = result['data']['name']
            live_status = result['data']['live_room']['liveStatus']

            if LIVING_STATUS_DICT.get(uid, None) is None:
                LIVING_STATUS_DICT[uid] = live_status
                logger.info('【查询直播状态】【{uname}】初始化'.format(uname=name))
                return

            if LIVING_STATUS_DICT.get(uid, None) != live_status:
                LIVING_STATUS_DICT[uid] = live_status

                room_id = result['data']['live_room']['roomid']
                room_title = result['data']['live_room']['title']
                room_cover_url = result['data']['live_room']['cover']

                if live_status == 1:
                    logger.info('【查询直播状态】【{name}】开播了，准备推送：{room_title}'.format(name=name, room_title=room_title))
                    push.push_for_bili_live(name, room_id, room_title, room_cover_url)


def get_headers(uid):
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'l=v;',
        'origin': 'https://space.bilibili.com',
        'pragma': 'no-cache',
        'referer': 'https://space.bilibili.com/{}/dynamic'.format(uid),
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }
