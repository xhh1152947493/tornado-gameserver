# -*- coding: utf-8 -*-

import redis

from configs import config
from utils import utils

_connect = None  # 共享的redis连接对象


def connect(redis_name):
	try:
		redis_info = config.get_config_by_key(redis_name)  # redis的数据
		return redis.StrictRedis(**redis_info)
	except Exception as data:
		print("Please set config of ", redis_name, data)


def share_connect() -> redis.StrictRedis:
	global _connect
	if not _connect:
		_connect = connect("db_redis")
	return _connect


def _hash_to_dict(data):
	result = dict()
	if not data:
		return result
	for k, v in list(data.items()):
		result[utils.bytes_to_str(k)] = utils.check_int(utils.bytes_to_str(v))
	return result
