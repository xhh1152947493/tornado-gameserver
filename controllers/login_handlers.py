# -*- coding: utf-8 -*-

import tornado.web

from configs import error
from utils import utils
from tornado.options import options

from .base_handler import BaseHandler


class WeChatLoginHandler(BaseHandler):
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
		if not self.get_string('params'):
			return self.write_json(error.DATA_BROKEN)

		params = utils.json_decode(self.get_string('params'))
		if not params or (not params.get('imei') and not params.get('mac')):
			return self.write_json(error.DATA_BROKEN)

		if params.get('code'):
			return self.__login_by_code(params.get('code'))

		if params.get('auto_token'):
			return self.__login_by_auto_token(params.get('auto_token'))

		return self.write_json(error.DATA_BROKEN)
