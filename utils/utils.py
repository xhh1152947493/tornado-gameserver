# -*- coding: utf-8 -*-
import hashlib
import json
import os
import random
import time
import requests
import urllib.parse

from defs import const
from tornado.httpclient import AsyncHTTPClient


def make_dir(path):
	"""创建目录"""
	return os.makedirs(path, 0o777, True)


def write(content, filename):
	# 写文件
	try:
		f = open(const.ROOT_PATH + filename, 'w')
		f.write(content)
		f.close()
	except Exception as data:
		print(data)
	return True


def log(filename, obj):  # 写日志文件
	try:
		f = open(const.ROOT_PATH + filename, 'a')
		f.write(time_mdh() + str(obj) + "\n")
		f.close()
	except Exception as data:
		print(data)
	return True


def read_json_file(filename):
	"""读json文件，并返回对应的对象，适用于小配置文件的读取"""
	try:
		with open(filename, encoding='utf-8') as js_file:
			obj = json.load(js_file)
			return obj
	except Exception as e:
		print("Failed to read JSON file:", filename, e)
		return {}


def json_decode(data):
	# 解析JSON数据，可以解析str或bytes
	try:
		if isinstance(data, bytes):
			data = data.decode('utf8')
		py_ret = json.loads(data)
		return py_ret, None
	except Exception as err:
		return None, err


def json_encode(data):
	# 从JSON中获取成对象,之所以要把此方法写在这里，请看文件开头的 reload 方法，这样才可以处理utf-8字符
	return str(json.dumps(data, ensure_ascii=False))


def time_mdh():
	return time.strftime("%m-%d %X ", time.localtime())


def time_format(format_str, time_stamp):
	return time.strftime(format_str, time.localtime(time_stamp))


def timestamp():  # 返回时间戳int型
	return int(time.time())


def str_to_int(data):
	# 从字符串转换成INT
	if not data:
		return 0
	try:
		return int(data)
	except Exception as data:
		print(data)
	return 0


def bytes_to_str(data):
	if isinstance(data, bytes):
		return data.decode('utf-8')
	return data


def check_int(data):
	if not isinstance(data, str):
		return data
	if not data.isdigit():
		return data
	return int(data)


def check_float(data):
	# 从字符串转换成double
	if not data:
		return 0.0
	try:
		return float(data)
	except Exception as data:
		print(data)
	return 0.0


def http_get(url, success_func, fail_func):
	# 注意要使用 tornado 启动APP后此函数才有效
	def handle_request(response):
		if response.body:
			success_func(response.body)
			return

		if response.error:
			fail_func()
		else:
			success_func(response.body)

	http_client = AsyncHTTPClient()
	params = {'method': 'GET'}
	http_client.fetch(url, handle_request, **params)


def http_post(url, post_params, success_func, fail_func, body=None):
	# 注意要使用 tornado 启动APP后此函数才有效
	def handle_request(response):
		if response.body:
			success_func(response.body)
			return

		if response.error:
			fail_func()
		else:
			success_func(response.body)

	http_client = AsyncHTTPClient()
	params = {'method': 'POST', 'body': '', 'validate_cert': False}
	if post_params:
		params['body'] = urllib.parse.urlencode(post_params)
	if body:
		params['body'] = body
	http_client.fetch(url, handle_request, **params)


def cos_upload(url, headers, file_params):
	""" 使用 requests 库 发送http请求 """
	try:
		http_resp = requests.post(url, None, headers=headers, verify=False, files=file_params)
		status_code = http_resp.status_code
		if status_code == 200 or status_code == 400:
			return http_resp.json()
		else:
			return "NETWORK_ERROR"
	except Exception as e:
		print(e)
		return "SERVER_ERROR"


def sha1(data):
	return hashlib.sha1(data.encode(encoding='UTF-8')).hexdigest()


def md5(data):
	return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()


def sha256(data):
	return hashlib.sha256(data.encode(encoding='UTF-8')).hexdigest()


_string_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c',
                'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C',
                'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def random_string(length=32):
	r_start, r_end = 0, len(_string_list) - 1
	result = ''
	for i in range(0, length - 1):
		result += _string_list[random.randint(r_start, r_end)]
	return result


class ObjectDict(dict):
	def __getattr__(self, name):
		try:
			return self[name]
		except KeyError:
			return None

	def __setattr__(self, name, value):
		self[name] = value
