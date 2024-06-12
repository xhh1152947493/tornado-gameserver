# -*- coding: utf-8 -*-

from . import table_name
from .db_sql import try_execute, try_get

from utils import utils


def _get(conn, uid):
	if not conn or uid <= 0:
		return {}
	sql = "SELECT * FROM `{0}` WHERE uid='{1}' LIMIT 1".format(table_name.TBL_ONLINE, uid)
	return try_get(conn, sql)


def get_token(conn, uid):
	data = _get(conn, uid)
	if not data:
		return ''
	return data.get('token')


def refresh_online(conn, uid):
	if not conn or uid <= 0:
		return {}

	inserts = dict()
	inserts['token'] = utils.random_string(40)
	inserts['login_time'] = utils.timestamp()

	insert_list = ["uid='{0}'".format(int(uid))]
	update_list = []
	for k, v in inserts.items():
		insert_list.append("{0}='{1}'".format(k, v))
		update_list.append("{0}='{1}'".format(k, v))

	sql = "INSERT INTO `{0}` SET " + ",".join(insert_list) + "ON DUPLICATE KEY UPDATE " + ",".join(update_list)
	sql = sql.format(table_name.TBL_ONLINE)

	try_execute(conn, sql)
	return inserts
