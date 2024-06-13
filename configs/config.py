# -*- coding: utf-8 -*-

import os
import logging

from tornado.options import define
from utils import utils

# json配置文件里面的所有数据
_jsonConfigs = utils.ReadJsonFile(
	os.path.dirname(
		os.path.realpath(__file__)) +
	'/config_debug.json')  # todo zhangzhihui 修改加载的文件

# 是否是开发模式中
IS_DEBUG = _jsonConfigs.get('is_debug')

# 杀进程前的等待时间
SHUTDOWN_WAIT_SECONDS = _jsonConfigs.get('shutdown_wait')

if IS_DEBUG:
	def GetLogLevel():
		return logging.DEBUG
else:
	def GetLogLevel():
		return logging.INFO


def GetConfigByKey(key):
	return _jsonConfigs.get(key)


# 微信开放平台APP_ID
define("wechatAppID", default="wxb4da0e0c73390eb0", help="微信开放平台APP_ID")
# 微信开放平台APP_SECRET
define("wechatAppSecret", default="178746f0f96386724f367ea7392158c5", help="微信开放平台APP_SECRET")
# 客户端签名key,http请求认证
define("appSignKey", default="2024CFD4-B5B1-4468-9ACE-60C3C6667B22", help="客户端http请求签名")
# 微信道具直购回调token
define("wechatPayToken", default="c59d612ds3f5c4215d9df26a", help="微信道具直购回调token")
# 微信直购AES key
define("wechatPayAESKey", default="asfxwd8i2b1234P1314UZZhYdAr7OCI6520ge2kfcXI", help="微信道具直购回调token")
