# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 12:33

import json
import mimetypes
import time
import uuid

from requests_toolbelt import MultipartEncoder
import util
from config import global_config
from logger import logger
import hashlib
import base64
import hmac


class Push(object):
    serverChan_enable = None
    serverChan_sckey = None
    serverChan_turbo_enable = None
    serverChan_turbo_SendKey = None
    wechat_enable = None
    wechat_corp_id = None
    wechat_agent_id = None
    wechat_corp_secret = None
    dingtalk_enable = None
    dingtalk_access_token = None

    def __init__(self):

        self.serverChan_enable = global_config.get_raw('push_serverChan', 'enable')
        self.serverChan_sckey = global_config.get_raw('push_serverChan', 'serverChan_SCKEY')
        self.serverChan_turbo_enable = global_config.get_raw('push_serverChan_turbo', 'enable')
        self.serverChan_turbo_SendKey = global_config.get_raw('push_serverChan_turbo', 'serverChan_SendKey')
        self.wechat_enable = global_config.get_raw('push_wechat', 'enable')
        self.wechat_corp_id = global_config.get_raw('push_wechat', 'corp_id')
        self.wechat_agent_id = global_config.get_raw('push_wechat', 'agent_id')
        self.wechat_corp_secret = global_config.get_raw('push_wechat', 'corp_secret')
        self.dingtalk_enable = global_config.get_raw('push_dingtalk', 'enable')
        self.dingtalk_access_token = global_config.get_raw('push_dingtalk', 'access_token')
        self.feishu_enable = global_config.get_raw('push_feishu', 'enable')
        self.feishu_appid = global_config.get_raw('push_feishu', 'appid')
        self.feishu_appsecret = global_config.get_raw('push_feishu', 'appsecret')
        self.feishu_receive_id_type = global_config.get_raw('push_feishu', 'receive_id_type')
        self.feishu_receive_id = global_config.get_raw('push_feishu', 'receive_id')
        self.feishu_template_id = global_config.get_raw('push_feishu', 'template_id')
    def push_for_bili_dynamic(self, uname=None, dynamic_id=None, content=None, pic_url=None, dynamic_type=None,
                              dynamic_time=None):
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
            logger.error(
                '【推送】缺少参数，uname:[{}]，dynamic_id:[{}]，content:[{}]'.format(uname, dynamic_id, content[:30]))
            return

        title_msg = '发动态了'
        if dynamic_type == 1:
            title_msg = '转发了动态'
        elif dynamic_type == 8:
            title_msg = '投稿了'
        title = '【{uname}】{dynamic_type}'.format(uname=uname, dynamic_type=title_msg)
        content = '{content}[{dynamic_time}]'.format(content=content[:100] + (content[100:] and '...'),
                                                     dynamic_time=dynamic_time)
        dynamic_url = 'https://www.bilibili.com/opus/{}'.format(dynamic_id)
        self._common_push(title, content, dynamic_url, pic_url)

    def push_for_bili_live(self, uname=None, room_id=None, room_title=None, room_cover_url=None):
        """
        B站直播提醒推送
        :param uname: up主名字
        :param room_id: 直播间id
        :param room_title: 直播间标题
        :param room_cover_url: 直播间封面
        """
        title = '【{uname}】开播了'.format(uname=uname)
        live_url = 'https://live.bilibili.com/{}'.format(room_id)
        self._common_push(title, room_title, live_url, room_cover_url)

    def _common_push(self, title, content, jump_url=None, pic_url=None):
        """
        :param title: 推送标题
        :param content: 推送内容
        :param jump_url: 跳转url
        :param pic_url: 图片url
        """
        if self.serverChan_enable == 'true':
            self._server_chan_push(title, content, jump_url)
        if self.serverChan_turbo_enable == 'true':
            self._server_chan_turbo_push(title, content, jump_url)
        if self.wechat_enable == 'true':
            access_token = self._get_wechat_access_token()
            self._wechat_push(access_token, title, content, jump_url, pic_url)
        if self.dingtalk_enable == 'true':
            self._dingtalk_push(title, content, jump_url, pic_url)
        if self.feishu_enable == 'true':
            self._feishu_push(title, content, jump_url, pic_url)

    def _server_chan_push(self, title, content, url=None):
        """
        推送(serverChan)
        :param title: 标题
        :param content: 内容
        :param url: 跳转地址
        """
        content = '`' + content + '`[点我直达]({url})'.format(url=url)
        push_url = 'https://sc.ftqq.com/{key}.send'.format(key=self.serverChan_sckey)
        response = util.requests_post(push_url, '推送_serverChan', params={"text": title, "desp": content})
        logger.info('【推送_serverChan】{msg}'.format(msg='成功' if util.check_response_is_ok(response) else '失败'))

    def _server_chan_turbo_push(self, title, content, url=None):
        """
        推送(serverChan_Turbo)
        :param title: 标题
        :param content: 内容
        :param url: 跳转地址
        """
        content = '`' + content + '`[点我直达]({url})'.format(url=url)
        push_url = 'https://sctapi.ftqq.com/{key}.send'.format(key=self.serverChan_turbo_SendKey)
        response = util.requests_post(push_url, '推送_serverChan_Turbo', params={"title": title, "desp": content})
        logger.info(
            '【推送_serverChan_Turbo】{msg}'.format(msg='成功' if util.check_response_is_ok(response) else '失败'))

    def _get_wechat_access_token(self):
        access_token = None
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'.format(
            corpid=self.wechat_corp_id, corpsecret=self.wechat_corp_secret)
        response = util.requests_get(url, '推送_wechat_获取access_tokon')
        if util.check_response_is_ok(response):
            result = json.loads(str(response.content, 'utf-8'))
            access_token = result['access_token']
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

        response = util.requests_post(push_url, '推送_wechat', params=params, data=json.dumps(body))
        logger.info('【推送_wechat】{msg}'.format(msg='成功' if util.check_response_is_ok(response) else '失败'))

    def _dingtalk_push(self, title, content, url=None, pic_url=None):
        """
        推送(dingtalk)
        :param title: 标题
        :param content: 内容
        :param url: 跳转url
        :param pic_url: 图片url
        """
        push_url = f'https://oapi.dingtalk.com/robot/send'
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": self.dingtalk_access_token
        }
        body = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": content,
                "messageUrl": url
            }
        }

        if pic_url is not None:
            body["link"]["picUrl"] = pic_url

        response = util.requests_post(push_url, '推送_dingtalk', headers=headers, params=params, data=json.dumps(body))
        logger.debug(response.json())
        logger.info('【推送_dingtalk】{msg}'.format(msg='成功' if util.check_response_is_ok(response) else '失败'))

    def _get_feishu_access_token(self):
        access_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        body = {
            "app_id": self.feishu_appid,
            "app_secret": self.feishu_appsecret
        }
        res = util.requests_post(access_url, headers=headers, data=json.dumps(body))
        return res.json()["tenant_access_token"]

    def _upload_feishu_image(self, pic_url):
        response = util.requests_get(pic_url)

        # 确保请求成功
        if response.status_code == 200:
            # 获取内容类型
            content_type = response.headers['Content-Type']
            # 根据内容类型推断扩展名
            extension = mimetypes.guess_extension(content_type)

            # 如果无法从内容类型推断扩展名，则默认使用.jpg
            if not extension:
                extension = '.jpg'

            # 构建保存文件的完整路径
            save_path_with_extension = str(uuid.uuid4()) + extension

            # 写入文件
            with open(save_path_with_extension, 'wb') as file:
                file.write(response.content)

            logger.info(f"Image saved as {save_path_with_extension}")

            url = "https://open.feishu.cn/open-apis/im/v1/images"
            form = {'image_type': 'message',
                    'image': (open(save_path_with_extension, 'rb'))}  # 需要替换具体的path
            multi_form = MultipartEncoder(form)
            headers = {'Authorization': "Bearer " + self._get_feishu_access_token(),
                       'Content-Type': multi_form.content_type}
            response = util.requests_post(url, headers=headers, data=multi_form)
            return response.json()["data"]["image_key"]
        else:
            logger.error(f"Failed to download image. Status code: {response.status_code}")

    def _feishu_push(self, title, content, url=None, pic_url=None):
        push_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=" + self.feishu_receive_id_type
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self._get_feishu_access_token()
        }
        body = {
            "type": "template",
            "data": {
                "template_id": self.feishu_template_id,
                "template_variable":
                    {
                        "pic": "img_v2_041b28e3-5680-48c2-9af2-497ace79333g",
                        "title": title,
                        "content": content,
                        "url": url
                    }
            }
        }
        if pic_url is not None:
            body["data"]["template_variable"]["pic"] = self._upload_feishu_image(pic_url)
        payload = json.dumps({
            "content": json.dumps(body),
            "msg_type": "interactive",
            "receive_id": self.feishu_receive_id
        })
        response = util.requests_post(push_url, '推送_feishu', headers=headers, data=payload)
        logger.debug(response)
        logger.info('【推送_feishu】{msg}'.format(msg='成功' if util.check_response_is_ok(response) else '失败'))


push = Push()
# push._feishu_push('test', 'test', 'https://baidu.com', 'test')
