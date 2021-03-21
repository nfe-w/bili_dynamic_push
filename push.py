# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 12:33

import requests
import json
from config import global_config
from logger import logger


class Push(object):
    serverChan_enable = None
    serverChan_sckey = None
    serverChan_turbo_enable = None
    serverChan_turbo_SendKey = None
    wechat_enable = None
    wechat_corp_id = None
    wechat_agent_id = None
    wechat_corp_secret = None

    def __init__(self):
        self.serverChan_enable = global_config.get_raw('push_serverChan', 'enable')
        self.serverChan_sckey = global_config.get_raw('push_serverChan', 'serverChan_SCKEY')
        self.serverChan_turbo_enable = global_config.get_raw('push_serverChan_turbo', 'enable')
        self.serverChan_turbo_SendKey = global_config.get_raw('push_serverChan_turbo', 'serverChan_SendKey')
        self.wechat_enable = global_config.get_raw('push_wechat', 'enable')
        self.wechat_corp_id = global_config.get_raw('push_wechat', 'corp_id')
        self.wechat_agent_id = global_config.get_raw('push_wechat', 'agent_id')
        self.wechat_corp_secret = global_config.get_raw('push_wechat', 'corp_secret')

    def push_msg(self, uname=None, dynamic_id=None, content=None, pic_url=None, dynamic_type=None, dynamic_time=None):
        """
        推送
        :param uname: up主名字
        :param dynamic_id: 动态id
        :param content: 动态内容
        :param pic_url: 动态图片
        :param dynamic_type: 动态类型
        :param dynamic_time: 动态发送时间
        """
        if uname is None or dynamic_id is None or content is None:
            logger.error('【推送】缺少参数，uname:[{}]，dynamic_id:[{}]，content:[{}]'.format(uname, dynamic_id, content[:30]))
            return

        title = '【{uname}】{dynamic_type}'.format(uname=uname, dynamic_type='投稿了' if dynamic_type == 8 else '发动态了')
        content = '{content}[{dynamic_time}]'.format(content=content[:100] + (content[100:] and '...'), dynamic_time=dynamic_time)

        if self.serverChan_enable == 'true':
            self._server_chan_push(dynamic_id, title, content)
        if self.serverChan_turbo_enable == 'true':
            self._server_chan_turbo_push(dynamic_id, title, content)
        if self.wechat_enable == 'true':
            access_token = self._get_wechat_access_token()
            self._wechat_push(access_token, dynamic_id, title, content, pic_url)

    def _server_chan_push(self, dynamic_id, title, content):
        """
        推送(serverChan)
        :param dynamic_id: 动态id
        :param title: 标题
        :param content: 内容
        """
        content = '`' + content + '`[点我直达](https://t.bilibili.com/{dynamic_id})'.format(dynamic_id=dynamic_id)
        push_url = 'https://sc.ftqq.com/{key}.send'.format(key=self.serverChan_sckey)
        response = requests.post(push_url, params={"text": title, "desp": content})
        logger.info('【推送_serverChan】{msg}，dynamic_id:[{dynamic_id}]'.format(
            msg='成功' if response.status_code == 200 else '失败', dynamic_id=dynamic_id))

    def _server_chan_turbo_push(self, dynamic_id, title, content):
        """
        推送(serverChan_Turbo)
        :param dynamic_id: 动态id
        :param title: 标题
        :param content: 内容
        """
        content = '`' + content + '`[点我直达](https://t.bilibili.com/{dynamic_id})'.format(dynamic_id=dynamic_id)
        push_url = 'https://sctapi.ftqq.com/{key}.send'.format(key=self.serverChan_turbo_SendKey)
        response = requests.post(push_url, params={"title": title, "desp": content})
        logger.info('【推送_serverChan_Turbo】{msg}，dynamic_id:[{dynamic_id}]'.format(
            msg='成功' if response.status_code == 200 else '失败', dynamic_id=dynamic_id))

    def _get_wechat_access_token(self):
        access_token = None
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'.format(
            corpid=self.wechat_corp_id, corpsecret=self.wechat_corp_secret)
        response = requests.get(url)
        if response.status_code == 200:
            result = json.loads(str(response.content, 'utf-8'))
            access_token = result['access_token']
        else:
            logger.info('【推送_wechat】获取access_token失败')
        return access_token

    def _wechat_push(self, access_token, dynamic_id, title, content, pic_url=None):
        """
        推送(wechat)
        :param access_token: 调用接口凭证
        :param dynamic_id: 动态id
        :param title: 标题
        :param content: 内容
        :param pic_url: 图片url
        """
        push_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            "access_token": access_token
        }
        body = {
            "touser": "@all",
            "agentid": self.wechat_agent_id,
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }

        if pic_url is None:
            body["msgtype"] = "textcard"
            body["textcard"] = {
                "title": title,
                "description": content,
                "url": 'https://t.bilibili.com/{}'.format(dynamic_id),
                "btntxt": "打开动态"
            }
        else:
            body["msgtype"] = "news"
            body["news"] = {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "url": 'https://t.bilibili.com/{}'.format(dynamic_id),
                        "picurl": pic_url
                    }
                ]
            }

        response = requests.post(push_url, params=params, data=json.dumps(body))
        logger.info('【推送_wechat】{msg}，dynamic_id:[{dynamic_id}]'.format(
            msg='成功' if response.status_code == 200 else '失败', dynamic_id=dynamic_id))


push = Push()
