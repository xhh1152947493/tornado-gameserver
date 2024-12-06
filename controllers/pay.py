# -*- coding: utf-8 -*-

import hmac
import hashlib

from tornado.options import options
from models import model
from .base_handler import CBaseHandler
from utils import utils, wx_crypt
from utils.log import Log
from data import error, const


def calc_pay_sig(uri, post_body, appkey):
	""" pay_sig签名算法
	  Args:
		  uri       - 当前请求的支付API的uri部分，不带query_string
					  例如：/wxa/game/getbalance、/wxa/game/pay
		  post_body - http POST的数据包体
		  appkey    - 对应环境的AppKey
	  Returns:
		  支付请求签名pay_sig
	"""
	need_sign_msg = uri + '&' + post_body
	pay_sig = hmac.new(key=appkey.encode('utf-8'), msg=need_sign_msg.encode('utf-8'),
	                   digestmod=hashlib.sha256).hexdigest()
	return pay_sig


def calc_signature(post_body, session_key):
	""" 用户登录态signature签名算法
	  Args:
		  post_body   - http POST的数据包体
		  session_key - 当前用户有效的session_key，参考auth.code2Session接口
	  Returns:
		  用户登录态签名signature
	"""
	need_sign_msg = post_body
	signature = hmac.new(key=session_key.encode('utf-8'), msg=need_sign_msg.encode('utf-8'),
	                     digestmod=hashlib.sha256).hexdigest()
	return signature


class CWxPayOrderCreateHandler(CBaseHandler):
	"""客户端请求订单创建,服务器生成唯一订单号"""

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
		dBody = utils.JsonDecode(self.request.body)
		if not dBody:
			return self.AnswerClient(error.ILLEGAL_PARAMS)
		if not dBody or not dBody.get("tradeID") or dBody.get("tradeID") == "" or not dBody.get(
				"productID") or dBody.get("productID") == "":
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		sSessionKey = model.GetSessionKeyByUID(self.ShareDB(), self.m_uid)
		if not sSessionKey:
			return self.AnswerClient(error.DB_OPERATE_ERR)

		sPaySign = calc_pay_sig(self.request.uri, self.request.body, options.wechatAppID)
		sSignature = calc_signature(self.request.body, sSessionKey)

		if model.CreatePayOrder(self.ShareDB(), dBody) != 1:
			return self.AnswerClient(error.DB_OPERATE_ERR)

		Log.info("create wechat pay order success. uid:{0} tradeID:{1}".format(self.m_uid, dBody.get("tradeID", '')))

		return self.AnswerClient(error.OK, {'tradeID': dBody.get("tradeID", ''), 'uid': self.m_uid, 'paySign': sPaySign,
		                                    'signature': sSignature})


def checkSignature(sSign, sTimestamp, sNoce):
	tmpList = [options.wechatPayToken, sTimestamp, sNoce]
	tmpList.sort()

	sTmp = ''.join(tmpList)
	sTmp = utils.SHA1(sTmp)

	return sTmp == sSign


class CWxPayRetPushHandler(CBaseHandler):
	"""wx官方推送订单消息,记录到数据库.多次推送只记录一次[同一个订单号,主键会重复]"""

	def prepare(self):
		# 检查消息是否来自wx
		self.m_signature = self.GetString("signature")
		self.m_timestamp = self.GetString("timestamp")
		self.m_nonce = self.GetString("nonce")
		self.m_msgSignature = self.GetString("msg_signature")

		if not checkSignature(self.m_signature, self.m_timestamp, self.m_nonce):
			return self.AnswerClient(-1, "check failed")

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def AnswerWechat(self):
		self.write({'ErrCode': 0, 'ErrMsg': "Success"})
		self.finish()

	def extract(self, dInfo):
		"""提取需要的数据"""
		dRet = dict()

		dRet['to_user_name'] = dInfo.get('ToUserName')
		dRet['from_user_name'] = dInfo.get('FromUserName')
		dRet['success_timestamp'] = dInfo.get('CreateTime')
		dRet['event'] = dInfo.get('Event')

		dMiniGame = dRet.get('MiniGame', {})
		sPayLoad = dMiniGame.get('Payload')
		sPayEventSig = dMiniGame.get('PayEventSig')

		dRet['is_mock'] = dMiniGame.get('IsMock')

		dPayLoad = utils.JsonDecode(sPayLoad)
		if dPayLoad:
			dRet['open_id'] = dPayLoad.get('OpenId')
			dRet['env'] = dPayLoad.get('Env')
			dRet['trade_id'] = dPayLoad.get('OutTradeNo')

			dGoodsInfo = dPayLoad.get('GoodsInfo', {})
			if dGoodsInfo:
				dRet['product_id'] = dGoodsInfo.get('ProductId')
				dRet['quantity'] = dGoodsInfo.get('Quantity')
				dRet['zone_id'] = dGoodsInfo.get('ZoneId')
				dRet['orig_price'] = dGoodsInfo.get('OrigPrice')
				dRet['actual_price'] = dGoodsInfo.get('ActualPrice')
				dRet['attach'] = dGoodsInfo.get('Attach')
				dRet['order_source'] = dGoodsInfo.get('OrderSource')

		return dRet

	def _request(self):
		oDecrypt = wx_crypt.WXBizMsgCrypt(options.wechatPayToken, options.wechatPayAESKey, options.wechatAppID)

		iRet, dDecryptJson = oDecrypt.DecryptMsg(self.request.body, self.m_msgSignature, self.m_signature, self.m_nonce)
		if iRet != wx_crypt.WXBizMsgCrypt_OK:
			return self.AnswerClient(-1, "check failed")

		dRet = self.extract(dDecryptJson)
		dRet['state'] = const.PAY_ORDER_STATE_DONE  # 设置为已支付状态

		if model.UpdatePayOrderByTradeID(self.ShareDB(), dRet) > 0:
			Log.info(f"pay order success, update success. trade_id:{dRet.get('trade_id')}")
		else:
			Log.info(f"pay order success, but update failed. trade_id:{dRet.get('trade_id')}")

		return self.AnswerWechat()


class CWxPayRewardReqHandler(CBaseHandler):
	"""客户端向服务器验证订单是否已经支付成功,验证成功则客户端发奖.服务器设置已发奖标记"""

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
		dParams = self.DecodeParams()
		sTradeID = dParams.get('tradeID')
		if not sTradeID:
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		if model.GetUidByTradeID(self.ShareDB(), sTradeID) != self.m_uid:
			return self.AnswerClient(error.SIGN_FAIL)

		if model.SetPayOrderRewarded(self.ShareDB(), sTradeID) != 1:
			Log.error(f"set pay order rewarded failed, uid:{self.m_uid} trade_id:{sTradeID}")
			return self.AnswerClient(error.DB_OPERATE_ERR)

		Log.error(f"set pay order rewarded success, uid:{self.m_uid} trade_id:{sTradeID}")
		return self.AnswerClient(error.OK, {'tradeID': sTradeID, 'uid': self.m_uid})


class CWxPayOrderQueryHandler(CBaseHandler):
	"""订单数据查询"""

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
		dParams = self.DecodeParams()
		sTradeID = dParams.get('tradeID')
		if not sTradeID:
			return self.AnswerClient(error.ILLEGAL_PARAMS)

		return self.AnswerClient(error.OK, model.GetOrderInfoByTradeID(self.ShareDB(), sTradeID))
