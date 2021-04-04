# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/24 19:11

import time

from config import global_config
from logger import logger
from proxy import my_proxy
from query_bili import query_dynamic
from query_bili import query_live_status

if __name__ == '__main__':
    enable_dynamic_push = global_config.get_raw('config', 'enable_dynamic_push')
    enable_living_push = global_config.get_raw('config', 'enable_living_push')
    uid_list = global_config.get_raw('config', 'uid_list').split(',')
    intervals_second = global_config.get_raw('config', 'intervals_second')
    intervals_second = int(intervals_second)
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
            my_proxy.current_proxy_ip = my_proxy.get_proxy()
            for _ in uid_list:
                if enable_dynamic_push == 'true':
                    query_dynamic(_)
                if enable_living_push == 'true':
                    query_live_status(_)
        time.sleep(intervals_second)
