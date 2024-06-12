# -*- coding: utf-8 -*-

from . import db_sql, table_name, model_gid
from .db_sql import try_get, try_execute
from utils import utils


def get_by_unionid(conn, unionid):
	if not conn or not unionid:
		return None

	sql = "SELECT * FROM `{0}` WHERE unionid='{1}' LIMIT 1".format(table_name.TBL_USER, unionid)
	return try_get(conn, sql)


def get_by_openid(conn, openid):
	if not conn or not openid:
		return None

	sql = "SELECT * FROM `{0}` WHERE openid='{1}' LIMIT 1".format(table_name.TBL_USER, openid)
	return try_get(conn, sql)


def get_by_auth_info(conn, auth_info):
	if not conn or not auth_info:
		return None

	rlt = get_by_unionid(conn, db_sql.escape(auth_info.get('unionid')))
	if rlt:
		return rlt

	return get_by_openid(conn, db_sql.escape(auth_info.get('openid')))


def _make_auto_token(unionid):
	return utils.sha1(unionid + utils.random_string(20))


def _make_wechat_cols(uid, params, auth_info):
	inserts = dict()
	# 用户唯一id
	inserts['uid'] = uid
	# 设备编号
	inserts['imei'] = db_sql.escape(params.get('imei'))
	# 设备地址
	inserts['mac'] = db_sql.escape(params.get('mac'))
	# 唯一token,可以根据这个直接登录账号
	inserts['auto_token'] = _make_auto_token(db_sql.escape(auth_info.get('unionid')))
	# wx唯一openid
	inserts['openid'] = db_sql.escape(auth_info.get('openid'))
	# wx唯一unionid
	inserts['unionid'] = db_sql.escape(auth_info.get('unionid'))
	# ip地址
	inserts['ip'] = params.get("ip") or 0
	return inserts


def create_new_user(conn, uid, params, auth_info):
	if not conn or not uid or not params or not auth_info:
		return None

	sql = db_sql.make_insert(table_name.TBL_USER, _make_wechat_cols(uid, params, auth_info))
	return try_execute(conn, sql)
