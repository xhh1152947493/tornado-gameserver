# -*- coding: utf-8 -*-


def KeysUserGameData():
	return "user_game_data"


def UpdateUserGameData(oRedisConn, iUID, bytesUserData):
	if not oRedisConn or iUID <= 0 or len(bytesUserData) == 0:
		return False

	return oRedisConn.hset(KeysUserGameData(), iUID, bytesUserData) > 0


def GetUpdatedUserList(oRedisConn):
	if not oRedisConn:
		return []

	return oRedisConn.hkeys(KeysUserGameData())


def DelUserGameData(oRedisConn, iUID):
	if not oRedisConn:
		return False

	return oRedisConn.hdel(KeysUserGameData(), iUID) > 0


def GetUserGameData(oRedisConn, iUID):
	if not oRedisConn:
		return b''

	return oRedisConn.hget(KeysUserGameData(), iUID)


def UpdateUserGameData2Mysql(oRedisConn):
	"""把内存数据写入mysql"""
	from .database import Connect
	from . import model

	oSqlConn = Connect('db_sql')
	if not oSqlConn or not oRedisConn:
		return

	uidList = GetUpdatedUserList(oRedisConn)
	for iUID in uidList:
		bytesUserData = GetUserGameData(oRedisConn, iUID)
		if len(bytesUserData) == 0:
			continue
		if model.UpdateUserGameDataByUID(oSqlConn, iUID, bytesUserData) == 0:
			continue

		DelUserGameData(oRedisConn, iUID)
