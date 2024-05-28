# -*- coding: utf-8 -*-

import tornado.web

from configs import error, const
from utils import utils
from tornado.options import options

from .base_handler import BaseHandler
from models import m_login, redis_keys


def gen_uid(conn_redis):
	if not conn_redis:
		return 0
	return const.INIT_UID + conn_redis.incr(redis_keys.keys_guid())


class GuestLoginHandler(BaseHandler):
	def prepare(self):
		pass

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def _request(self):
		params = self.decode_params()
		if not params:
			return self.write_json(error.ILLEGAL_PARAMS)
		imei = params.get('imei')
		if not imei or not isinstance(imei, str):
			return self.write_json(error.ILLEGAL_PARAMS)

		return self._login_by_guest(imei)

	def _new_user_login(self, conn, conn_redis, imei):
		uid = gen_uid(conn_redis)
		if not m_login.insert_new_user(conn, uid, imei):
			return self.write_json(error.DB_OPERATE_ERR)

		return self.write_json(error.OK)

	def _login_by_guest(self, imei):
		conn = self.share_db()
		if not conn:
			return self.write_json(error.DB_CONNECT_ERR)
		conn_redis = self.share_redis()
		if not conn_redis:
			return self.write_json(error.DB_CONNECT_ERR)

		uid = m_login.get_uid_by_imei(conn, imei)
		if not uid:  # 新角色登录流程
			return self._new_user_login(conn, conn_redis, imei)

		bs = conn_redis.get(redis_keys.keys_player_game(uid))
		if not bs:
			return self.write_json(error.DATA_NOT_FOUND)

		return self.write_json(error.OK, bs)


class WeChatLoginHandler(BaseHandler):
	def prepare(self):
		pass

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	@tornado.web.asynchronous
	def __login_by_code(self, code):
		if not self.share_db():
			return self.write_json(error.SYSTEM_ERR)

		url = "https://api.weixin.qq.com/sns/oauth2/access_token" \
		      "?appid={0}&secret={1}&code={2}&grant_type=authorization_code"
		url = url.format(options.we_chat_app_id, options.we_chat_app_secret, code)

		def success_func(data):
			pass

		def failed_func():
			self.write_json(error.SYSTEM_ERR)

		utils.http_get(url, success_func, failed_func)

	@tornado.web.asynchronous
	def __login_by_auto_token(self, auto_token):
		return self.write_json(error.SYSTEM_ERR)

	def _request(self):
		params = self.decode_params()
		if not params or (not params.get('imei') and not params.get('mac')):
			return self.write_json(error.ILLEGAL_PARAMS)

		if params.get('code'):
			return self.__login_by_code(params.get('code'))

		if params.get('auto_token'):
			return self.__login_by_auto_token(params.get('auto_token'))

		return self.write_json(error.ILLEGAL_PARAMS)
