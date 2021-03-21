# Bili_Dynamic_Push

## 声明:

- 本仓库发布的`bili_dynamic_push`项目中涉及的任何脚本，仅用于测试和学习研究，禁止用于商业用途
- `yr-wan` 对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害
- 以任何方式查看此项目的人或直接或间接使用`bili_dynamic_push`项目的任何脚本的使用者都应仔细阅读此声明
- `bili_dynamic_push` 保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或`bili_dynamic_push`项目，则视为已接受此免责声明
- 本项目遵循`MIT LICENSE`协议，如果本声明与`MIT LICENSE`协议有冲突之处，以本声明为准

## 简介

定时检测指定up的动态，如果发生变化进行推送

## 运行环境

- [Python 3](https://www.python.org/)

## 使用教程

#### 1. 填写config.ini配置信息

(1)`config`下的参数

- `uid_list`为需要扫描的up主uid列表，使用英文逗号分隔，必填
- `intervals_second`为扫描间隔秒数，不建议过于频繁，必填
- `begin_time`为扫描开始时间，非必填，不支持跨日期
- `end_time`为扫描停止时间，非必填，不支持跨日期

(2)`push_serverChan`下的参数

- `enable`是否启用serverChan推送
- `serverChan_SCKEY`推送必须填入 serverChan_SCKEY，如何获取请参考 http://sc.ftqq.com/3.version

#### 2.安装第三方库

`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

#### 3.启动脚本

`nohup python3 -u bili_dynamic_push.py >& bili_dynamic_push.log &`
