# -*- coding: utf-8 -*-

from .base_handler import CBaseHandler
from data import error
from models import model
from utils.log import Log


class CActiveRedeemCode(CBaseHandler):
	"""兑换码兑奖,兑换码的添加应该在后台操作"""

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
		sCode = self.DecodeParams().get('code')
		if not sCode:
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		if not model.ValidateRedeemCode(self.ShareDB(), sCode):
			Log.warning(f"redeem code:{sCode} illegal, uid:{self.m_uid}")
			return self.AnswerClient(error.REDEEMCODE_ERR)

		if not model.ValidateRedeemCodeRewarded(self.ShareDB(), self.m_uid, sCode):
			return self.AnswerClient(error.REDEEMCODE_ALREADY)

		if model.InsertRedeemCodeRewardedRecord(self.ShareDB(), self.m_uid, sCode) != 1:
			Log.error(f"redeem code insert to code rewarded db failed. code:{sCode} uid:{self.m_uid}")
			return self.AnswerClient(error.DB_OPERATE_ERR)

		if model.UpdateRedeemCode(self.ShareDB(), sCode) != 1:
			Log.error(f"redeem code insert to code db failed. code:{sCode} uid:{self.m_uid}")

		Log.info(f"redeem code rewarded success. code:{sCode} uid:{self.m_uid}")
		return self.AnswerClient(error.OK, {'code': sCode, 'uid': self.m_uid})
