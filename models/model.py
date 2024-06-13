# -*- coding: utf-8 -*-

from .database import *
from data import const, table_name
from utils import utils


def IncrGID(oConn):
	"""uid,唯一id生成器"""
	if not oConn:
		return 0

	sSQL = "INSERT INTO `{0}` (id, counter_value) VALUES (1, 1) ON DUPLICATE KEY UPDATE counter_value=counter_value+1".format(
		table_name.TBL_GID)
	if TryExecuteRowcount(oConn, sSQL) <= 0:
		return 0

	oRet = TryGet(oConn, "SELECT `counter_value` FROM `{0}` WHERE id=1 LIMIT 1".format(table_name.TBL_GID))
	if not oRet or oRet.get("counter_value") is None:
		return 0

	return oRet["counter_value"] + const.INIT_GID


def GetSignToken(oConn, iUID):
	"""从online表获取token,检查请求的合法性"""
	if not oConn:
		return ""

	sSQL = "SELECT `token` FROM `{0}` WHERE uid='{1}' LIMIT 1".format(table_name.TBL_ONLINE, iUID)
	oRet = TryGet(oConn, sSQL)
	if not oRet:
		return ""

	return oRet["token"]


def GetUserInfoByUnionID(oConn, sUnionID):
	if not oConn or sUnionID == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE union_id='{1}' LIMIT 1".format(table_name.TBL_USER, sUnionID)
	return TryGet(oConn, sSQL)


def GetUserInfoByOpenID(oConn, sOpenID):
	if not oConn or sOpenID == "":
		return None

	sSQL = "SELECT * FROM `{0}` WHERE open_id='{1}' LIMIT 1".format(table_name.TBL_USER, sOpenID)
	return TryGet(oConn, sSQL)


def GetUserInfoByAuthInfo(oConn, dAuthInfo):
	"""根据unionid和openid从user表获取获取用户数据"""
	if not oConn or not dAuthInfo:
		return None

	dRet = GetUserInfoByUnionID(oConn, Escape(dAuthInfo.get('unionid')))
	if dRet:
		return dRet

	return GetUserInfoByOpenID(oConn, Escape(dAuthInfo.get('openid')))


def _makeAutoToken(sUnionID):
	return utils.SHA1(sUnionID + utils.RandomString(20))


def CreateWxUser(oConn, iUID, dParams, dAuthInfo):
	"""创建wx用户"""
	if not oConn or iUID <= 0 or not dParams or not dAuthInfo:
		return None

	sUnionID = dAuthInfo.get('unionid')
	sOpenID = dAuthInfo.get('openid')
	if not sUnionID or not sOpenID:
		return None

	dInserts = dict()
	dInserts['uid'] = iUID
	dInserts['imei'] = Escape(dParams.get('imei', ""))
	dInserts['mac'] = Escape(dParams.get('mac', ""))
	dInserts['union_id'] = Escape(sUnionID)
	dInserts['open_id'] = Escape(sOpenID)
	dInserts['auto_token'] = _makeAutoToken(sUnionID)

	return TryExecuteRowcount(oConn, FormatInsert(table_name.TBL_USER, dInserts))


def RefreshOnline(oConn, dUserInfo, dAuthInfo):
	"""存在就更新,不存在就插入"""
	if not oConn or not dUserInfo or not dAuthInfo:
		return None

	iUID = dUserInfo.get('uid')
	if not iUID:
		return None

	dInserts = dict()
	dInserts['token'] = utils.RandomString(40)
	dInserts['login_time'] = utils.Timestamp()
	dInserts['session_key'] = Escape(dAuthInfo.get('session_key', ''))

	insertList = ["uid='{0}'".format(int(iUID))]
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

	sSQL = f"SELECT `choice_env` FROM {table_name.TBL_SWITCH} WHERE id=1"

	oRet = TryGet(oConn, sSQL)
	if not oRet:
		return 0

	return oRet['choice_env']


def CreatePayOrder(oConn, sTradeID, iEnv):
	if not oConn or sTradeID == "":
		return 0

	dInserts = dict()
	dInserts['trade_id'] = sTradeID
	dInserts['create_timestamp'] = utils.Timestamp()
	dInserts['env'] = iEnv
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
	       f"=b.open_id WHERE a.trade_id={sTradeID} "

	oRet = TryGet(oConn, sSQL)
	if not oRet:
		return 0

	return oRet['uid']


def SetPayOrderRewarded(oConn, sTradeID):
	if not oConn:
		return 0

	sSQL = "UPDATE `{0}` SET `state`={1} WHERE `state`={2} and `trade_id`={3}".format(table_name.TBL_ORDER,
	                                                                                  const.PAY_ORDER_STATE_REWARDED,
	                                                                                  const.PAY_ORDER_STATE_DONE,
	                                                                                  sTradeID)

	return TryExecuteRowcount(oConn, sSQL)


def GetOrderInfoByTradeID(oConn, sTradeID):
	if not oConn:
		return None

	sSQL = "SELECT * FROM {0} WHERE `trade_id`={1}".format(table_name.TBL_ORDER, sTradeID)

	return TryGet(oConn, sSQL)
