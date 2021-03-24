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
        B站动态提醒推送
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

        title_msg = '发动态了'
        if dynamic_type == 1:
            title_msg = '转发了动态'
        elif dynamic_type == 8:
            title_msg = '投稿了'
        title = '【{uname}】{dynamic_type}'.format(uname=uname, dynamic_type=title_msg)
        content = '{content}[{dynamic_time}]'.format(content=content[:100] + (content[100:] and '...'), dynamic_time=dynamic_time)
        dynamic_url = 'https://t.bilibili.com/{}'.format(dynamic_id)

        if self.serverChan_enable == 'true':
            self._server_chan_push(title, content, dynamic_url)
        if self.serverChan_turbo_enable == 'true':
            self._server_chan_turbo_push(title, content, dynamic_url)
        if self.wechat_enable == 'true':
            access_token = self._get_wechat_access_token()
            self._wechat_push(access_token, title, content, dynamic_url, pic_url)

    def _server_chan_push(self, title, content, url=None):
        """
        推送(serverChan)
        :param title: 标题
        :param content: 内容
        :param url: 跳转地址
        """
        content = '`' + content + '`[点我直达]({url})'.format(url=url)
        push_url = 'https://sc.ftqq.com/{key}.send'.format(key=self.serverChan_sckey)
        try:
            response = requests.post(push_url, params={"text": title, "desp": content})
        except Exception as e:
            logger.error("【推送_serverChan】：{}".format(e))
            return
        logger.info('【推送_serverChan】{msg}'.format(msg='成功' if response.status_code == 200 else '失败'))

    def _server_chan_turbo_push(self, title, content, url=None):
        """
        推送(serverChan_Turbo)
        :param title: 标题
        :param content: 内容
        :param url: 跳转地址
        """
        content = '`' + content + '`[点我直达]({url})'.format(url=url)
        push_url = 'https://sctapi.ftqq.com/{key}.send'.format(key=self.serverChan_turbo_SendKey)
        try:
            response = requests.post(push_url, params={"title": title, "desp": content})
        except Exception as e:
            logger.error("【推送_serverChan_Turbo】：{}".format(e))
            return
        logger.info('【推送_serverChan_Turbo】{msg}'.format(msg='成功' if response.status_code == 200 else '失败'))

    def _get_wechat_access_token(self):
        access_token = None
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'.format(
            corpid=self.wechat_corp_id, corpsecret=self.wechat_corp_secret)
        try:
            response = requests.get(url)
        except Exception as e:
            logger.error("【推送_wechat】获取access_token：{}".format(e))
            return
        if response.status_code == 200:
            result = json.loads(str(response.content, 'utf-8'))
            access_token = result['access_token']
        else:
            logger.info('【推送_wechat】获取access_token失败')
        return access_token

    def _wechat_push(self, access_token, title, content, url=None, pic_url=None):
        """
        推送(wechat)
        :param access_token: 调用接口凭证
        :param title: 标题
        :param content: 内容
        :param url: 跳转url
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
                "url": url,
                "btntxt": "打开详情"
            }
        else:
            body["msgtype"] = "news"
            body["news"] = {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "url": url,
                        "picurl": pic_url
                    }
                ]
            }

        try:
            response = requests.post(push_url, params=params, data=json.dumps(body))
        except Exception as e:
            logger.error("【推送_wechat】：{}".format(e))
            return
        logger.info('【推送_wechat】{msg}'.format(msg='成功' if response.status_code == 200 else '失败'))


push = Push()
