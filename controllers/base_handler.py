# -*- coding: utf-8 -*-

import tornado
import sys

from models import database
from models import base_redis
from configs import error
from utils.log import logger

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
		self.uid = 0
		self.platform = 0
		self.__sql_conn = None
		self.__redis_conn = None

	def prepare(self):
		logger.debug("recv client request: %s", self.request.uri)

	def share_db(self):
		if self.__sql_conn:
			return self.__sql_conn
		conn = database.connect("db_sql")
		if not conn:
			return None
		self.__sql_conn = conn
		return conn

	def share_redis(self):
		if self.__redis_conn:
			return self.__redis_conn
		conn = base_redis.share_connect()
		if not conn:
			return None
		self.__redis_conn = conn
		return conn

	# 获得整型参数
	def get_int(self, name):
		try:
			return int(self.get_argument(name, 0))
		except Exception as e:
			print(e)
			return 0

	# 获得字符串参数
	def get_string(self, name):
		return self.get_argument(name, '')

	# 回答客户端
	def write_json(self, code, data=None):
		# 如果有报错的话,把报错调用的地方返回给客户端
		fr = sys._getframe(1)
		desc = f"{fr.f_code.co_name}:{fr.f_lineno}" if code != error.OK else ""
		self.write({'code': code, 'err_info': desc, 'data': data or []})
		self.finish()
