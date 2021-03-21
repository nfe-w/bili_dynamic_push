# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 12:33

import requests
from config import global_config
from logger import logger


class Push(object):
    serverChan_enable = None
    serverChan_sckey = None

    def __init__(self):
        self.serverChan_enable = global_config.get_raw('push_serverChan', 'enable')
        self.serverChan_sckey = global_config.get_raw('push_serverChan', 'serverChan_SCKEY')

    def push_msg(self, uname=None, dynamic_id=None, content=None, dynamic_type=None, dynamic_time=None):
        """
        推送
        :param uname: up主名字
        :param dynamic_id: 动态id
        :param content: 动态内容
        :param dynamic_type: 动态类型
        :param dynamic_time: 动态发送时间
        """
        if uname is None or dynamic_id is None or content is None:
            logger.error('【推送】缺少参数，uname:[{}]，dynamic_id:[{}]，content:[{}]'.format(uname, dynamic_id, content[:30]))
            return

        title = '【{uname}】{dynamic_type}'.format(uname=uname, dynamic_type='投稿了' if dynamic_type == 8 else '发动态了')
        content = '`{content}[{dynamic_time}]`[点我直达](https://t.bilibili.com/{dynamic_id})'.format(
            content=content[:100] + (content[100:] and '...'), dynamic_time=dynamic_time, dynamic_id=dynamic_id)

        if self.serverChan_enable == 'true':
            self._server_chan(dynamic_id, title, content)

    def _server_chan(self, dynamic_id, title, content):
        """
        推送(serverChan)
        :param dynamic_id: 动态id
        :param title: 标题
        :param content: 内容
        """
        push_url = 'https://sc.ftqq.com/{key}.send'.format(key=self.serverChan_sckey)
        response = requests.post(push_url, params={"text": title, "desp": content})
        logger.info('【推送_serverChan】{msg}，dynamic_id:[{dynamic_id}]'.format(
            msg='成功' if response.status_code == 200 else '失败', dynamic_id=dynamic_id))


push = Push()
