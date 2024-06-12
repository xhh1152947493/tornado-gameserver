# -*- coding: utf-8 -*-

import tornado.web

from tornado.options import options
from defs import error, const
from models import model_online, model_player, model_gid
from .base_handler import CBaseHandler
from utils import utils


class CWxLoginHandler(CBaseHandler):
	def prepare(self):
		# 登录阶段无需携带uid进行请求
		if not self.check_fixed_params(False):
			return self.write_json(error.ILLEGAL_PARAMS)
		# 登录阶段无需token验证http请求合法
		if not self.check_sign_no_token():
			return self.write_json(error.SIGN_FAIL)

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	@tornado.web.asynchronous
	def __login_by_code(self, params):
		"""微信登录凭证校验,异步操作数据库不要串了"""
		code = params['code']
		url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
			options.we_chat_app_id, options.we_chat_app_secret, code)

		def suc_func(data):
			auth_info, err = utils.json_decode(data)
			if err is not None or auth_info.get("errcode") != 0:
				return self.write_json(error.HTTP_REQ_ERR)

			user_info = model_player.get_by_auth_info(self.share_db(), auth_info)
			if not user_info:  # 新角色
				uid = model_gid.incr_gid(self.share_db())
				if uid <= 0:
					return self.write_json(error.DB_OPERATE_ERR)
				if model_player.create_new_user(self.share_db(), uid, params, auth_info) <= 0:
					return self.write_json(error.DB_OPERATE_ERR)
				user_info = model_player.get_by_auth_info(self.share_db(), auth_info)  # 再次获取数据,此时肯定能获取到
				if not user_info:
					return self.write_json(error.DB_OPERATE_ERR)

			info = model_online.refresh_online(self.share_db(), user_info["uid"])
			return self.write_json(error.OK, {
				"uid": user_info["uid"],
				"user_data": user_info["user_data"],
				"token": info["token"],
			})

		def fail_func():
			self.write_json(error.HTTP_REQ_ERR)

		utils.http_get(url, suc_func, fail_func)

	def _request(self):
		params = self.decode_params()
		if not params or not params.get('imei') or not params.get('mac') or not params.get('code'):
			return self.write_json(error.ILLEGAL_PARAMS)

		return self.__login_by_code(params)
