# -*- coding: utf-8 -*-

from pymysql.converters import escape_string
from configs import config
from utils.torndb import Connection
from utils.log import Log


# 连接数据库
def Connect(sName):
	try:
		infoDict = config.GetConfigByKey(sName)  # 中心的数据
		return Connection(**infoDict)
	except Exception as e:
		Log.error(f"connect mysql failed, name:{sName}, err:{e}")


# 防止sql注入攻击
def Escape(obj):
	if type(obj) is int:
		return obj
	if type(obj) is float:
		return obj
	if obj is None:
		return ''
	if type(obj) is bool:
		return int(obj)
	if not obj:
		return ''
	return escape_string(obj)


def EscapeDict(dParams):
	for k, v in dParams.items():
		if v and isinstance(v, str):
			dParams[k] = Escape(v)


def FormatInsert(sTable, dParams):
	insertList = []
	for k, v in dParams.items():
		insertList.append(r"`{0}`='{1}'".format(k, v))

	insrtStr = ", ".join(insertList)

	sql = "INSERT INTO `{0}` SET {1}".format(sTable, insrtStr)
	return sql


def FormatUpdate(sTable, dParams, sCondition):
	updateList = []
	for k, v in dParams.items():
		updateList.append(r"`{0}`='{1}'".format(k, v))

	sUpdate = ", ".join(updateList)

	sql = "UPDATE `{0}` SET {1} WHERE {2}".format(sTable, sUpdate, sCondition)
	return sql


def FormatQuery(sTable, lstFiled, sCondition):
	sQuery = ", ".join([f"`{field}`" for field in lstFiled])

	sql = "SELECT {0} FROM `{1}` WHERE {2}".format(sQuery, sTable, sCondition)
	return sql


def FormatDelete(sTable, sCondition):
	sql = "DELETE FROM `{0}` WHERE {1}".format(sTable, sCondition)
	return sql


def TryGet(oConn, sSql):
	try:
		rlt = oConn.get(sSql)
		return rlt
	except Exception as e:
		Log.error(f"execute sql failed 1, err:{e}\nsql:{sSql}")
		return None


def TryExecute(oConn, sSql):
	try:
		rlt = oConn.execute(sSql)
		return rlt
	except Exception as e:
		Log.error(f"execute sql failed 2, err:{e}\nsql:{sSql}")
		return None


def TryExecuteRowcount(oConn, sSql):
	try:
		rlt = oConn.execute_rowcount(sSql)
		return rlt
	except Exception as e:
		Log.error(f"execute sql failed 3, err:{e}\nsql:{sSql}")
		return None
