# -*- coding: utf-8 -*-

import urllib.parse
import tornado
import tornado.web
import sys

from models import database, model
from utils import utils
from utils.log import Log
from data import error
from tornado.options import options


class CBaseHandler(tornado.web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
		self.m_uid = 0
		self.m_conn = None

	# 对象销毁时会自动调用db.close(),这里无需再显示调用了
	def on_finish(self):
		if self.m_conn:
			self.m_conn.close()

	def ShareDB(self):
		if self.m_conn:
			return self.m_conn
		conn = database.Connect("db_sql")
		if not conn:
			return None
		self.m_conn = conn
		return conn

	def CheckFixedParams(self, bWithUID=True):
		if bWithUID and not self.GetInt('uid'):
			return False

		return True

	def SetupFixedParams(self):
		self.m_uid = self.GetInt('uid') or 0

	@staticmethod
	def _validateSign(dParams, sSign, sToken=""):
		signObj = dParams.get("sign")
		if not signObj:
			return False

		sCheckSign = signObj[0].decode(encoding='UTF-8')
		if not sCheckSign or len(sCheckSign) < 1:
			return False

		valuesList = []
		for sKey in sorted(list(dParams.keys())):  # 按字典key排序
			if sKey == "sign":
				continue
			tmpStr = dParams[sKey][0].decode(encoding='UTF-8')
			valuesList.append(sKey + '=' + urllib.parse.quote_plus(tmpStr))

		valuesList.append("key={0}".format(sSign))

		if sToken and len(sToken) > 0:
			valuesList.append("token={0}".format(sToken))

		sSignData = "&".join(valuesList)

		return utils.MD5(sSignData) == sCheckSign

	def CheckSign(self):
		"""验证参数的正确性, 验证请求的合法性"""
		sToken = model.GetSignToken(self.ShareDB(), int(self.get_argument("uid")))
		bSignPassed = self._validateSign(self.request.arguments, options.appSignKey, sToken)
		if bSignPassed:
			self.SetupFixedParams()
		return bSignPassed

	def CheckSignNoToken(self):
		"""单纯验证参数正确性"""
		bSignPassed = self._validateSign(self.request.arguments, options.appSignKey)
		if bSignPassed:
			self.SetupFixedParams()
		return bSignPassed

	# 获得整型参数
	def GetInt(self, sName):
		try:
			return int(self.get_argument(sName, 0))
		except Exception as e:
			Log.error(f"get int param failed, name:{sName} err:{e}")
			return 0

	# 获得字符串参数
	def GetString(self, sName):
		return self.get_argument(sName, '')

	def DecodeParams(self):
		sOrgParams = self.GetString('params')
		if not sOrgParams:
			return None
		return utils.JsonDecode(sOrgParams)

	# 回答客户端
	def AnswerClient(self, code, data=None):
		"""如果有错误的话,把报错调用的地方返回给客户端"""
		fr = sys._getframe(1)
		desc = f"{fr.f_code.co_name}:{fr.f_lineno}" if code != error.OK else ""
		self.write({'code': code, 'err': desc, 'data': data or []})
		self.finish()
