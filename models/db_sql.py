# -*- coding: utf-8 -*-
import pymysql

from configs import config
from utils.torndb import Connection, Row
from utils import utils


# 连接数据库
def connect(db_name):
	try:
		db_info = config.get_config_by_key(db_name)  # 中心的数据
		return Connection(**db_info)
	except Exception as data:
		print("Please set config of ", db_name, data)


def resume_bool(data):
	if 'false' == data:
		return False
	if 'true' == data:
		return True
	return data


def resume_int(data):
	if type(data) is not str:
		return data
	if data.isdigit():
		return int(data)
	return data


# 防止sql注入攻击
def escape(data):
	if type(data) is int:
		return data
	if type(data) is float:
		return data
	if data is None:
		return ''
	if type(data) is bool:
		return int(data)
	if not data:
		return ''
	return pymysql.escape_string(data)


def is_string(data):
	return isinstance(data, str)


def escape_dict(params):
	for k, v in params.items():
		if v and is_string(v):
			params[k] = escape(v)


def split_to_list(string_data):
	if not string_data:
		return []
	tmp = string_data.split(',')
	ret = []
	for item in tmp:
		ret.append(utils.str_to_int(item))
	return ret


def dict_to_row(dict_obj):
	return Row(dict_obj)


def make_insert(table_name, params):
	insert_list = []
	for k, v in params.items():
		insert_list.append("`{0}`='{1}'".format(k, v))
	sql = "INSERT INTO `{0}` SET " + ",".join(insert_list)
	sql = sql.format(table_name)
	return sql


def make_update(table_name, params, condition):
	update_list = []
	for k, v in params.items():
		update_list.append("`{0}`='{1}'".format(k, v))
	update_str = ", ".join(update_list)
	sql = "UPDATE `{0}` SET {1} WHERE {2}".format(table_name, update_str, condition)
	return sql


def make_query(table_name, fileds, condition):
	query_str = ", ".join([f"`{field}`" for field in fileds])
	sql = "SELECT {0} FROM `{1}` WHERE {2}".format(query_str, table_name, condition)
	return sql


def make_delete(table_name, condition):
	sql = "DELETE FROM `{0}` WHERE {1}".format(table_name, condition)
	return sql
