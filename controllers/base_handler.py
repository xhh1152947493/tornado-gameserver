# -*- coding: utf-8 -*-

import tornado
import tornado.web
import sys

from models import db_sql
from models import db_redis
from configs import error
from utils import utils
from utils.log import logger


class CBaseHandler(tornado.web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
		self.uid = 0
		self.platform = 0
		self.__conn = None
		self.__redis_conn = None

	def share_db(self):
		if self.__conn:
			return self.__conn
		conn = db_sql.connect("db_sql")
		if not conn:
			return None
		self.__conn = conn
		return conn

	def share_redis(self):
		if self.__redis_conn:
			return self.__redis_conn
		conn = db_redis.share_connect()
		if not conn:
			return None
		self.__redis_conn = conn
		return conn

	# 对象销毁时会自动调用db.close(),这里无需再显示调用了
	def on_finish(self):
		pass

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

	def decode_params(self):
		org_params = self.get_string('params')
		if not org_params:
			return None
		rlt, err = utils.json_decode(org_params)
		if err:
			logger.error("decode json params failed. data:%s err:%s", org_params, err)
		return rlt

	# 回答客户端
	def write_json(self, code, data=None):
		# 如果有错误的话,把报错调用的地方返回给客户端
		fr = sys._getframe(1)
		desc = f"{fr.f_code.co_name}:{fr.f_lineno}" if code != error.OK else ""
		self.write({'code': code, 'err_info': desc, 'data': data or []})
		self.finish()
