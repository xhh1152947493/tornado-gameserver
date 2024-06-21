# -*- coding: utf-8 -*-

import urllib.parse
import tornado
import tornado.web
import sys

from models import database, model, base_redis
from utils import utils
from utils.log import Log
from data import error
from tornado.options import options

_nonce_record = {}
_nonce_max_duration = 300


def checkRepeatNonceReq(bNonce, iTimestamp, sToken):
	"""客户端与服务器的时间不能误差过大,如果客户端修改了本地时间则拒绝请求"""
	iNow = utils.Timestamp()

	keyList = list(_nonce_record.keys())
	for key in keyList:
		if iNow > _nonce_record[key] + _nonce_max_duration:
			_nonce_record.pop(key)

	if bNonce in _nonce_record:
		Log.error(
			f"http reqeust repeat nonce attack!!! nonce:{bNonce} timestamp:{iTimestamp} now:{iNow} token:{sToken}")
		return False

	if abs(iNow - iTimestamp) > _nonce_max_duration:
		Log.error(
			f"http reqeust timestamp   illegal!!! nonce:{bNonce} timestamp:{iTimestamp} now:{iNow} token:{sToken}")
		return False

	_nonce_record[bNonce] = iTimestamp
	return True


class CBaseHandler(tornado.web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
		self.m_uid = 0
		self.m_conn = None
		self.m_redis_conn = None

	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
		self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

	def options(self):
		# 处理预检请求
		self.set_status(204)
		self.finish()

	# 对象销毁时会自动调用db.close(),这里无需再显示调用了
	def on_finish(self):
		pass

	def ShareDB(self):
		if self.m_conn:
			return self.m_conn
		conn = database.Connect("db_sql")
		if not conn:
			return None
		self.m_conn = conn  # mysql只有一个引用对象,请求结束后会自动销毁close
		return conn

	def ShareRedis(self):
		if self.m_redis_conn:
			return self.m_redis_conn
		conn = base_redis.ShareConnect()
		if not conn:
			return None
		self.m_redis_conn = conn  # redis有一个全局的引用对象,请求结束后不会自动销毁close
		return conn

	def CheckFixedParams(self, bWithUID=True):
		if bWithUID and not self.GetInt('uid'):
			return False

		return True

	def SetupFixedParams(self):
		self.m_uid = self.GetInt('uid') or 0

	@staticmethod
	def validateSign(dParams, sSign, sToken=""):
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
		sTrueSign = utils.MD5(sSignData)

		bRet = sTrueSign == sCheckSign
		if bRet:  # 验证通过再检查是否重放攻击
			nonceList = dParams.get("nonce")
			if not nonceList or len(nonceList[0]) != 16:
				return False

			timestampList = dParams.get("timestamp")
			if not timestampList:
				return False

			if not checkRepeatNonceReq(nonceList[0], int(timestampList[0].decode(encoding='UTF-8')), sToken):
				return False

		return bRet

	def CheckSign(self):
		"""验证参数的正确性, 验证请求的合法性"""
		sToken = model.GetSignToken(self.ShareDB(), int(self.get_argument("uid")))
		if sToken == "":
			return False
		bSignPassed = self.validateSign(self.request.arguments, options.appSignKey, sToken)
		if bSignPassed:
			self.SetupFixedParams()
		return bSignPassed

	def CheckSignNoToken(self):
		"""单纯验证参数正确性"""
		bSignPassed = self.validateSign(self.request.arguments, options.appSignKey)
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
