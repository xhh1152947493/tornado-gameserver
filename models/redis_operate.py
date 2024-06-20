# -*- coding: utf-8 -*-


def KeysUserGameData():
	return "user_game_data"


def UpdateUserGameData(oRedisConn, uid, bytesUserData):
	if not oRedisConn or uid <= 0 or len(bytesUserData) == 0:
		return False

	return oRedisConn.hset(KeysUserGameData(), uid, bytesUserData) > 0


def GetUpdatedUserList(oRedisConn):
	if not oRedisConn:
		return []

	return oRedisConn.hkeys(KeysUserGameData())


def DelUserGameData(oRedisConn, uid):
	if not oRedisConn:
		return False

	return oRedisConn.hdel(KeysUserGameData(), uid) > 0


def GetUserGameData(oRedisConn, uid):
	if not oRedisConn:
		return b''

	return oRedisConn.hget(KeysUserGameData(), uid)


def UpdateUserGameData2Mysql(oRedisConn):
	"""把内存数据写入mysql"""
	from .database import Connect
	from . import model

	oSqlConn = Connect('db_sql')
	if not oSqlConn or not oRedisConn:
		return

	uidList = GetUpdatedUserList(oRedisConn)
	for uid in uidList:
		bytesUserData = GetUserGameData(oRedisConn, uid)
		if len(bytesUserData) == 0:
			continue
		if model.UpdateUserGameDataByUID(oSqlConn, uid, bytesUserData) == 0:
			continue

		DelUserGameData(oRedisConn, uid)
