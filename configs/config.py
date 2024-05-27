# -*- coding: utf-8 -*-

import os
import logging

from tornado.options import define
from utils import utils

# json配置文件里面的所有数据
_json_items = utils.read_json_file(
	os.path.dirname(
		os.path.realpath(__file__)) +
	'/config.json')

# 是否是开发模式中
IS_DEBUG = _json_items.get('is_debug')

# 杀进程前的等待时间
if IS_DEBUG:
	SHUTDOWN_WAIT_SECONDS = 1


	def get_log_level():
		return logging.DEBUG

else:
	SHUTDOWN_WAIT_SECONDS = 30


	def get_log_level():
		return logging.INFO


def get_config_by_key(key):
	return _json_items.get(key)


# 微信开放平台APP_ID
define("we_chat_app_id", default="wxb4da0e0c73390eb0", help="微信开放平台APP_ID")
# 微信开放平台APP_SECRET
define("we_chat_app_secret", default="178746f0f96386724f367ea7392158c5", help="微信开放平台APP_SECRET")
