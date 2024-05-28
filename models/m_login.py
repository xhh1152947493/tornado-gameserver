# -*- coding: utf-8 -*-


from . import table_name
from . import db_sql


def get_uid_by_imei(conn, imei):
	if not conn or not imei:
		return None

	sql = db_sql.make_query(table_name.TABLE_USER, ["uid"], "`{0}`='{1}' LIMIT 1".format("imei", imei))
	rlt = conn.query(sql)
	if not rlt:
		return None

	return rlt[0].get("uid")


def insert_new_user(conn, uid, imei):
	if not conn or not imei or not uid:
		return False

	sql = db_sql.make_insert(table_name.TABLE_USER, {
		"uid": uid,
		"imei": imei,
	})
	rlt = conn.execute(sql)

	return rlt and rlt > 0
