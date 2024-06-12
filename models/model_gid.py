# -*- coding: utf-8 -*-

from . import table_name
from .db_sql import try_execute, try_get
from defs import const


def incr_gid(conn):
	"""固定id为1"""
	if not conn:
		return 0

	sql = "INSERT INTO `{0}` (id, counter_value) VALUES (1, 1) ON DUPLICATE KEY UPDATE counter_value=counter_value+1".format(
		table_name.TBL_GID)
	if try_execute(conn, sql) <= 0:
		return 0

	sql = "SELECT `counter_value` FROM `{0}` WHERE id=1 LIMIT 1".format(table_name.TBL_GID)
	rlt = try_get(conn, sql)
	if not rlt or rlt.get("counter_value") is None:
		return 0

	return rlt["counter_value"] + const.INIT_GID
