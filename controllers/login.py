# -*- coding: utf-8 -*-

import tornado.web

from tornado.options import options
from data import error
from models import model
from .base_handler import CBaseHandler
from utils import utils


class CWxLoginHandler(CBaseHandler):
	def prepare(self):
		if not self.CheckSignNoToken():  # 登录阶段无需token验证http请求合法
			return self.AnswerClient(error.SIGN_FAIL)

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def FormatLoginReturn(self, dOnlineInfo, dUserInfo, dAuthInfo):
		return self.AnswerClient(error.OK, {
			"uid": dUserInfo["uid"],
			"token": dOnlineInfo["token"],
			"data": dUserInfo["data"],
		})

	@tornado.web.asynchronous
	def LoginByCode(self, dParams):
		"""微信登录凭证校验,异步操作数据库不要串了"""
		sCode = dParams['code']
		sURL = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
			options.wechatAppID, options.wechatAppSecret, sCode)

		def successFunc(sRet):
			dAuthInfo = sRet
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
			dOnlineInfo = model.RefreshOnline(oConn, dUserInfo, dAuthInfo)
			if not dOnlineInfo:
				return self.AnswerClient(error.DB_OPERATE_ERR)

			return self.FormatLoginReturn(dOnlineInfo, dUserInfo, dAuthInfo)

		def failedFunc():
			self.AnswerClient(error.HTTP_REQ_ERR)

		utils.HttpGet(sURL, successFunc, failedFunc)

	def _request(self):
		dParams = self.DecodeParams()
		if not dParams.get('code'):
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		return self.LoginByCode(dParams)
