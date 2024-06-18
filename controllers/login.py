# -*- coding: utf-8 -*-

import tornado.web

from tornado.options import options

import configs.config
from data import error
from models import model
from .base_handler import CBaseHandler
from utils import utils
from utils.log import Log


class CBaseLoginHandler(CBaseHandler):
	def prepare(self):
		if not self.CheckSignNoToken():  # 登录阶段无需token验证http请求合法
			return self.AnswerClient(error.SIGN_FAIL)

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def _request(self):
		pass

	def FormatLoginReturn(self, dOnlineInfo, dUserInfo, dAuthInfo=None):
		dRet = {
			"uid": dUserInfo["uid"],
			"token": dOnlineInfo["token"],  # 用于验证后续http请求
			"data": dUserInfo["data"],  # 玩家数据
			"openID": dUserInfo.get("open_id", "")
		}
		return self.AnswerClient(error.OK, dRet)


class CAutoTokenLoginHandler(CBaseLoginHandler):
	"""使用autoToken指定登录"""

	def LoginByAutoToken(self, dParams):
		sAutoToken = dParams['autoToken']

		dUserInfo = model.GetUserInfoByAutoToken(self.ShareDB(), sAutoToken)
		if not dUserInfo:  # 没有登录失败
			return self.AnswerClient(error.DATA_NOT_FOUND)

		# 登录
		dOnlineInfo = model.RefreshOnline(self.ShareDB(), dUserInfo["uid"])
		if not dOnlineInfo:
			return self.AnswerClient(error.DB_OPERATE_ERR)

		Log.info("user auto token login success. uid:{0}".format(dUserInfo["uid"]))
		return self.FormatLoginReturn(dOnlineInfo, dUserInfo)

	def _request(self):
		dParams = self.DecodeParams()
		if not dParams.get('autoToken'):
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		return self.LoginByAutoToken(dParams)


class CGuestLoginHandler(CBaseLoginHandler):
	"""游客登录"""

	def LoginByIMEI(self, dParams):
		oConn = self.ShareDB()
		if not oConn:
			return self.AnswerClient(error.DB_CONNECT_ERR)

		sIMEI = dParams['imei']

		dUserInfo = model.GetUserInfoByIMEI(self.ShareDB(), sIMEI)
		if not dUserInfo:  # 创建新角色
			iUID = model.IncrGID(oConn)
			if iUID <= 0:
				return self.AnswerClient(error.DB_OPERATE_ERR)
			if model.CreateGuestUser(oConn, iUID, dParams) != 1:
				return self.AnswerClient(error.DB_OPERATE_ERR)
			dUserInfo = model.GetUserInfoByIMEI(self.ShareDB(), sIMEI)
			if not dUserInfo:
				return self.AnswerClient(error.DB_OPERATE_ERR)

		# 登录
		dOnlineInfo = model.RefreshOnline(oConn, dUserInfo["uid"])
		if not dOnlineInfo:
			return self.AnswerClient(error.DB_OPERATE_ERR)

		Log.info("user guest login success. uid:{0}".format(dUserInfo["uid"]))
		return self.FormatLoginReturn(dOnlineInfo, dUserInfo)

	def _request(self):
		if not configs.config.IS_DEBUG:  # 正式环境禁止游客登录
			return self.AnswerClient(error.SYSTEM_ERR)

		dParams = self.DecodeParams()
		if not dParams.get('imei'):
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		return self.LoginByIMEI(dParams)


class CWxLoginHandler(CBaseLoginHandler):
	"""微信登录"""

	@tornado.web.asynchronous
	def LoginByCode(self, dParams):
		"""微信登录凭证校验,异步操作数据库不要串了"""
		sCode = dParams['code']
		sURL = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
			options.wechatAppID, options.wechatAppSecret, sCode)

		def successFunc(sRet):
			dAuthInfo = utils.JsonDecode(sRet)
			if not dAuthInfo or dAuthInfo.get("errcode") != 0:  # 微信验证失败
				return self.AnswerClient(error.HTTP_REQ_ERR)

			oConn = self.ShareDB()
			if not oConn:
				return self.AnswerClient(error.DB_CONNECT_ERR)

			dUserInfo = model.GetUserInfoByAuthInfo(oConn, dAuthInfo)
			if not dUserInfo:  # 创建新角色
				iUID = model.IncrGID(oConn)
				if iUID <= 0:
					return self.AnswerClient(error.DB_OPERATE_ERR)
				if model.CreateWxUser(oConn, iUID, dParams, dAuthInfo) != 1:
					return self.AnswerClient(error.DB_OPERATE_ERR)
				dUserInfo = model.GetUserInfoByAuthInfo(oConn, dAuthInfo)  # 再次获取数据,此时肯定能获取到
				if not dUserInfo:
					return self.AnswerClient(error.DB_OPERATE_ERR)

			# 登录
			dOnlineInfo = model.RefreshOnline(oConn, dUserInfo["uid"], dAuthInfo.get('session_key', ''))
			if not dOnlineInfo:
				return self.AnswerClient(error.DB_OPERATE_ERR)

			Log.info("user wechat login success. uid:{0}".format(dUserInfo["uid"]))
			return self.FormatLoginReturn(dOnlineInfo, dUserInfo, dAuthInfo)

		def failedFunc():
			self.AnswerClient(error.HTTP_REQ_ERR)

		utils.HttpGet(sURL, successFunc, failedFunc)

	def _request(self):
		dParams = self.DecodeParams()
		if not dParams.get('code'):
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		return self.LoginByCode(dParams)
