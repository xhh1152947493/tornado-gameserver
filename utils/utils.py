# -*- coding: utf-8 -*-

import hashlib
import json
import sys
import random
import time
import urllib.parse

from tornado.httpclient import AsyncHTTPClient


def ReadJsonFile(sFileName):
	"""读json文件，并返回对应的对象，适用于小配置文件的读取"""
	try:
		with open(sFileName, encoding='utf-8') as oFile:
			obj = json.load(oFile)
			return obj
	except Exception as e:
		from .log import Log

		Log.error(f"read json file failed, file:{sFileName}, err:{e}", sFileName, e)
		return {}


def JsonDecode(obj):
	"""解析JSON数据，可以解析str或bytes"""
	try:
		if isinstance(obj, bytes):
			obj = obj.decode('utf8')
		ret = json.loads(obj)
		return ret
	except Exception as err:
		from .log import Log

		fr = sys._getframe(1)
		Log.error(f"decode json failed, {fr.f_code.co_name}:{fr.f_lineno}. data:{obj} err:{err}")
		return None


def JsonEncode(obj):
	"""从JSON中获取成对象,之所以要把此方法写在这里，请看文件开头的 reload 方法，这样才可以处理utf-8字符"""
	return str(json.dumps(obj, ensure_ascii=False))


def TimeMdh():
	return time.strftime("%m-%d %X ", time.localtime())


def TimeFormat(format_str, time_stamp):
	return time.strftime(format_str, time.localtime(time_stamp))


def Timestamp():  # 返回时间戳int型
	return int(time.time())


def Bytes2Str(obj):
	if isinstance(obj, bytes):
		return obj.decode('utf-8')
	return obj


def HttpGet(sURL, successFunc, failedFunc):
	"""注意要使用 tornado 启动APP后此函数才有效"""

	def _request(oResp):
		if oResp.body:
			successFunc(oResp.body)
			return
		if oResp.error:
			failedFunc()
		else:
			successFunc(oResp.body)

	dParams = {'method': 'GET'}

	oHttpClient = AsyncHTTPClient()
	oHttpClient.fetch(sURL, _request, **dParams)


def HttpPost(sURL, sPostParams, successFunc, failedFunc, oBody=None):
	"""注意要使用 tornado 启动APP后此函数才有效"""

	def _request(oResp):
		if oResp.body:
			successFunc(oResp.body)
			return
		if oResp.error:
			failedFunc()
		else:
			successFunc(oResp.body)

	dParams = {'method': 'POST', 'body': '', 'validate_cert': False}
	if sPostParams:
		dParams['body'] = urllib.parse.urlencode(sPostParams)
	if oBody:
		dParams['body'] = oBody

	oHttpClient = AsyncHTTPClient()
	oHttpClient.fetch(sURL, _request, **dParams)


def SHA1(sData):
	return hashlib.sha1(sData.encode(encoding='UTF-8')).hexdigest()


def MD5(sData):
	return hashlib.md5(sData.encode(encoding='UTF-8')).hexdigest()


def SHA256(sData):
	return hashlib.sha256(sData.encode(encoding='UTF-8')).hexdigest()


_stringList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c',
               'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
               'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C',
               'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def RandomString(iLen):
	iStart, iEnd = 0, len(_stringList) - 1

	sRet = ''
	for i in range(0, iLen - 1):
		sRet += _stringList[random.randint(iStart, iEnd)]

	return sRet


class objectDict(dict):
	def __getattr__(self, name):
		try:
			return self[name]
		except KeyError:
			return None

	def __setattr__(self, name, value):
		self[name] = value
