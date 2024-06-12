# -*- coding: utf-8 -*-
import ipaddress
import urllib.parse
import tornado
import tornado.web
import sys

from models import db_sql, model_online
from models import db_redis
from utils import utils
from utils.log import log
from defs import error
from tornado.options import options


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

	def check_fixed_params(self, with_uid=True):
		if with_uid and not self.get_int('uid'):
			return False

		return True

	def setup_fixed_params(self):
		self.uid = self.get_int('uid') or 0
		self.platform = self.get_int('platform')

	@staticmethod
	def _check_sign(params, sign, token=""):
		sign_obj = params.get("sign")
		if not sign_obj:
			return False

		check_sign = sign_obj[0].decode(encoding='UTF-8')
		if not check_sign or len(check_sign) < 1:
			return False

		keys = list(params.keys())
		keys.sort()
		values = []

		for k in keys:
			if k == "sign":
				continue
			tmp_str = params[k][0].decode(encoding='UTF-8')
			values.append(k + '=' + urllib.parse.quote_plus(tmp_str))
		values.append("key={0}".format(sign))
		if token and len(token) > 0:
			values.append("token={0}".format(token))

		sign_data = "&".join(values)
		return utils.md5(sign_data) == check_sign

	def check_sign(self):
		"""验证参数的正确性, 验证请求的合法性"""
		uid = int(self.get_argument("uid"))
		token = model_online.get_token(self.share_db(), uid)
		sign_passed = self._check_sign(self.request.arguments, options.app_sign_key, token)
		if sign_passed:
			self.setup_fixed_params()
		return sign_passed

	def check_sign_no_token(self):
		"""单纯验证参数正确性"""
		sign_passed = self._check_sign(self.request.arguments, options.app_sign_key)
		if sign_passed:
			self.setup_fixed_params()
		return sign_passed

	# 对象销毁时会自动调用db.close(),这里无需再显示调用了
	def on_finish(self):
		pass

	def get_int_ip(self):
		int_ip = 0
		try:
			int_ip = int(ipaddress.ip_address(self.request.remote_ip))
		except ValueError:
			pass
		return int_ip

	# 获得整型参数
	def get_int(self, name):
		try:
			return int(self.get_argument(name, 0))
		except Exception as e:
			log.error(f"get int param failed, {e}")
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
			log.error("decode json params failed. data:%s err:%s", org_params, err)
		return rlt

	# 回答客户端
	def write_json(self, code, data=None):
		# 如果有错误的话,把报错调用的地方返回给客户端
		fr = sys._getframe(1)
		desc = f"{fr.f_code.co_name}:{fr.f_lineno}" if code != error.OK else ""
		self.write({'code': code, 'err': desc, 'data': data or []})
		self.finish()
