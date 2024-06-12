# -*- coding: utf-8 -*-

import os
import logging

from tornado.options import define
from utils import utils

# json配置文件里面的所有数据 todo zhangzhihui 修改加载的文件
_json_items = utils.read_json_file(
	os.path.dirname(
		os.path.realpath(__file__)) +
	'/config_debug.json')

# 是否是开发模式中
IS_DEBUG = _json_items.get('is_debug')

# 杀进程前的等待时间
SHUTDOWN_WAIT_SECONDS = _json_items.get('shutdown_wait')

if IS_DEBUG:
	def get_log_level():
		return logging.DEBUG
else:
	def get_log_level():
		return logging.INFO


def get_config_by_key(key):
	return _json_items.get(key)


# 微信开放平台APP_ID
define("we_chat_app_id", default="wxb4da0e0c73390eb0", help="微信开放平台APP_ID")
# 微信开放平台APP_SECRET
define("we_chat_app_secret", default="178746f0f96386724f367ea7392158c5", help="微信开放平台APP_SECRET")
# 客户端签名key,http请求认证
define("app_sign_key", default="2024CFD4-B5B1-4468-9ACE-60C3C6667B22", help="")
