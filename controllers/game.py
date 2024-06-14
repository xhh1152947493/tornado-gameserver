# -*- coding: utf-8 -*-

from data import error
from models import model
from .base_handler import CBaseHandler
from utils.log import Log


class CUploadUserDataHandler(CBaseHandler):
	"""客户端上传玩家数据,1分钟上传一次.重要数据立即上传"""

	def prepare(self):
		if not self.CheckFixedParams():
			return self.AnswerClient(error.ILLEGAL_PARAMS)
		if not self.CheckSign():
			return self.AnswerClient(error.SIGN_FAIL)

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def _request(self):
		bytesUserData = self.request.body
		if not isinstance(bytesUserData, bytes):  # 客户端直接上传加密后的二进制玩家数据
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		# Todo zhangzhihui 如果数据量大的话需要考虑缓存并保证安全性.目前先直接写入mysql并观察延迟情况
		if model.UpdateUserGameDataByUID(self.ShareDB(), self.m_uid, bytesUserData) != 1:
			Log.error(f"update user game data failed. uid:{self.m_uid}")
			return self.AnswerClient(error.DB_OPERATE_ERR)

		Log.info(f"update user game data success. uid:{self.m_uid}")
		return self.AnswerClient(error.OK, {'uid': self.m_uid})
