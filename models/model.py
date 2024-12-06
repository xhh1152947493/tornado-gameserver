# -*- coding: utf-8 -*-

from .database import *
from data import const, table_name
from utils import utils


def incrCounter(oConn, _id):
	if not oConn:
		return 0

	sSQL = "INSERT INTO `{0}` (id, counter_value) VALUES ({1}, 1) ON DUPLICATE KEY UPDATE counter_value=counter_value+1".format(
		table_name.TBL_COUNTER, _id)
	if TryExecuteRowcount(oConn, sSQL) <= 0:
		return 0

	oRet = TryGet(oConn, "SELECT `counter_value` FROM `{0}` WHERE id={1} LIMIT 1".format(table_name.TBL_COUNTER, _id))
	if not oRet or oRet.get("counter_value") is None:
		return 0

	return oRet["counter_value"]


def IncrGID(oConn):
	"""uid,唯一id生成器"""
	iValue = incrCounter(oConn, const.COUNTER_ID_FOR_GID)

	return iValue + const.INIT_GID if iValue > 0 else 0


def IncrTradeID(oConn):
	"""tradeID,唯一id生成器"""
	iValue = incrCounter(oConn, const.COUNTER_ID_FOR_TRADE_ID)

	return iValue + const.INIT_TRADE_ID if iValue > 0 else 0


def GetSignToken(oConn, uid):
	"""从online表获取token,检查请求的合法性"""
	if not oConn:
		return ""

	sSQL = "SELECT `token` FROM `{0}` WHERE uid='{1}' LIMIT 1".format(table_name.TBL_ONLINE, uid)
	oRet = TryGet(oConn, sSQL)
	if not oRet or not oRet["token"]:
		return ""

	return oRet["token"]


def GetUserInfoByAutoToken(oConn, sAutoToken):
	if not oConn or sAutoToken == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE auto_token='{1}' LIMIT 1".format(table_name.TBL_USER, Escape(sAutoToken))
	return TryGet(oConn, sSQL)


def GetUserInfoByIMEI(oConn, sIMEI):
	if not oConn or sIMEI == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE imei='{1}' LIMIT 1".format(table_name.TBL_USER, Escape(sIMEI))
	return TryGet(oConn, sSQL)


def CreateGuestUser(oConn, uid, dParams):
	"""创建游客用户"""
	if not oConn or uid <= 0 or not dParams:
		return 0

	dInserts = dict()
	dInserts['uid'] = uid
	dInserts['imei'] = Escape(dParams.get('imei', ""))
	dInserts['mac'] = Escape(dParams.get('mac', ""))
	dInserts['auto_token'] = makeAutoToken(dInserts['imei'])
	dInserts['open_id'] = Escape(utils.RandomString(40))
	dInserts['union_id'] = Escape(utils.RandomString(40))

	return TryExecuteRowcount(oConn, FormatInsert(table_name.TBL_USER, dInserts))


def GetUserInfoByUnionID(oConn, sUnionID):
	if not oConn or sUnionID == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE union_id='{1}' LIMIT 1".format(table_name.TBL_USER, Escape(sUnionID))
	return TryGet(oConn, sSQL)


def GetUserInfoByOpenID(oConn, sOpenID):
	if not oConn or sOpenID == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE open_id='{1}' LIMIT 1".format(table_name.TBL_USER, Escape(sOpenID))
	return TryGet(oConn, sSQL)


def GetUserInfoByAuthInfo(oConn, dAuthInfo):
	"""根据unionid和openid从user表获取获取用户数据"""
	if not oConn or not dAuthInfo:
		return None

	dRet = GetUserInfoByUnionID(oConn, dAuthInfo.get('unionid'))
	if dRet:
		return dRet

	return GetUserInfoByOpenID(oConn, dAuthInfo.get('openid'))


def makeAutoToken(sUnionID):
	return utils.SHA1(sUnionID + utils.RandomString(20))


def CreateWxUser(oConn, uid, dParams, dAuthInfo):
	"""创建wx用户"""
	if not oConn or uid <= 0 or not dParams or not dAuthInfo:
		return 0

	sUnionID = dAuthInfo.get('unionid')
	sOpenID = dAuthInfo.get('openid')
	if not sUnionID or not sOpenID:
		return 0

	dInserts = dict()
	dInserts['uid'] = uid
	dInserts['imei'] = Escape(dParams.get('imei', ""))
	dInserts['mac'] = Escape(dParams.get('mac', ""))
	dInserts['union_id'] = Escape(sUnionID)
	dInserts['open_id'] = Escape(sOpenID)
	dInserts['auto_token'] = makeAutoToken(sUnionID)

	return TryExecuteRowcount(oConn, FormatInsert(table_name.TBL_USER, dInserts))


def RefreshOnline(oConn, uid, sSessionKey=""):
	"""存在就更新,不存在就插入"""
	if not oConn:
		return None

	dInserts = dict()
	dInserts['token'] = utils.RandomString(40)
	dInserts['login_time'] = utils.Timestamp()
	dInserts['session_key'] = Escape(sSessionKey)

	insertList = ["uid='{0}'".format(int(uid))]
	updateList = []
	for k, v in dInserts.items():
		insertList.append("{0}='{1}'".format(k, v))
		updateList.append("{0}='{1}'".format(k, v))

	sSQL = f"INSERT INTO `{table_name.TBL_ONLINE}` SET " + ",".join(insertList) + "ON DUPLICATE KEY UPDATE " + ",".join(
		updateList)

	if TryExecuteRowcount(oConn, sSQL) <= 0:
		return None

	return dInserts


def GetPayEnv(oConn):
	if not oConn:
		return 0

	sSQL = f"SELECT `choice_env` FROM {table_name.TBL_SWITCH} LIMIT 1"

	oRet = TryGet(oConn, sSQL)
	if not oRet or not oRet['choice_env']:
		return 0

	return oRet['choice_env']


def GetSessionKeyByUID(oConn, uid):
	if not oConn:
		return ""

	sSQL = f"SELECT `session_key` FROM {table_name.TBL_ONLINE} WHERE `uid`={uid} LIMIT 1 "

	oRet = TryGet(oConn, sSQL)
	if not oRet or not oRet['session_key']:
		return ""

	return oRet['session_key']


def CreatePayOrder(oConn, dBody):
	if not oConn or not dBody:
		return 0

	dInserts = dict()
	dInserts['trade_id'] = Escape(dBody.get("tradeID", ''))
	dInserts['product_id'] = Escape(dBody.get("productID", ''))
	dInserts['create_timestamp'] = utils.Timestamp()
	dInserts['env'] = Escape(dBody.get("env", ''))
	dInserts['state'] = const.PAY_ORDER_STATE_IDLE

	sSQL = FormatInsert(table_name.TBL_ORDER, dInserts)

	return TryExecuteRowcount(oConn, sSQL)


def UpdatePayOrderByTradeID(oConn, dInfo):
	"""支付成功,更新订单数据"""
	if not oConn or not dInfo:
		return 0

	sTradeID = dInfo.get('trade_id')
	if not sTradeID:
		return 0

	dUpdate = dict()
	for k, v in dInfo.items():
		if v is None or v == sTradeID:
			continue
		dUpdate[k] = v

	sSQL = FormatUpdate(table_name.TBL_ORDER, dUpdate, f"`trade_id`={sTradeID}")

	return TryExecuteRowcount(oConn, sSQL)


def GetUidByTradeID(oConn, sTradeID):
	if not oConn:
		return 0

	sSQL = f"SELECT {table_name.TBL_USER}.uid FROM {table_name.TBL_USER} a JOIN {table_name.TBL_ORDER} b ON a.open_id" \
	       f"=b.open_id WHERE a.trade_id={Escape(sTradeID)} "

	oRet = TryGet(oConn, sSQL)
	if not oRet or not oRet['uid']:
		return 0

	return oRet['uid']


def SetPayOrderRewarded(oConn, sTradeID):
	if not oConn:
		return 0

	sSQL = "UPDATE `{0}` SET `state`={1} WHERE `state`={2} and `trade_id`={3}".format(table_name.TBL_ORDER,
	                                                                                  const.PAY_ORDER_STATE_REWARDED,
	                                                                                  const.PAY_ORDER_STATE_DONE,
	                                                                                  Escape(sTradeID))

	return TryExecuteRowcount(oConn, sSQL)


def GetOrderInfoByTradeID(oConn, sTradeID):
	if not oConn:
		return None

	sSQL = "SELECT * FROM {0} WHERE `trade_id`={1}".format(table_name.TBL_ORDER, Escape(sTradeID))

	return TryGet(oConn, sSQL)


def UpdateUserGameDataByUID(oConn, uid, bytesUserData):
	if not oConn:
		return 0

	# 先转成16进制,再用UNHEX把16进制转换成2进制写入
	sSQL = "UPDATE `{0}` SET `data`=UNHEX('{1}') WHERE `uid`={2} LIMIT 1".format(table_name.TBL_USER,
	                                                                             bytesUserData.hex(), uid)

	return TryExecuteRowcount(oConn, sSQL)


def ValidateRedeemCode(oConn, sCode):
	if not oConn or not sCode:
		return False

	sSQL = "SELECT 1 FROM {0} WHERE `code`={1} LIMIT 1".format(table_name.TBL_CODE, Escape(sCode))

	oRet = TryGet(oConn, sSQL)
	if not oRet or 1 not in oRet:
		return False

	return True


def UpdateRedeemCode(oConn, sCode):
	if not oConn or not sCode:
		return 0

	sSQL = FormatUpdate(table_name.TBL_CODE, {
		'count': 'count+1'
	}, "`code`={0}".format(Escape(sCode)))

	return TryExecuteRowcount(oConn, sSQL)


def ValidateRedeemCodeRewarded(oConn, uid, sCode):
	"""表格逐渐增大有隐患,添加索引以提高查询速度,两个字段组合起来成为唯一索引"""
	if not oConn or not sCode:
		return False

	sSQL = "SELECT 1 FROM {0} WHERE `uid` = {1} `code`={2} LIMIT 1".format(table_name.TBL_CODE_REWARDED, uid,
	                                                                       Escape(sCode))

	oRet = TryGet(oConn, sSQL)
	if not oRet or 1 not in oRet:  # 记录存在表示已经领取过建立了
		return True

	return False


def InsertRedeemCodeRewardedRecord(oConn, uid, sCode):
	if not oConn or not uid or not sCode:
		return 0

	sSQL = FormatInsert(table_name.TBL_CODE_REWARDED, {
		'uid': uid,
		'code': Escape(sCode)
	})

	return TryExecuteRowcount(oConn, sSQL)
