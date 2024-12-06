# -*- coding: utf-8 -*-

import redis

from configs import config

_connect = None  # 共享的redis连接对象


def Connect(sName):
	try:
		dInfo = config.GetConfigByKey(sName)  # redis的数据
		return redis.StrictRedis(**dInfo)
	except Exception as e:
		from utils.log import Log
		Log.error(f"connect redis failed, name:{sName}, err:{e}")
		return None


def ShareConnect() -> redis.StrictRedis:
	global _connect
	if not _connect:
		_connect = Connect("db_redis")
	return _connect
