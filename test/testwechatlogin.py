# -*- coding: utf-8 -*-
import urllib.parse

from utils import utils

if __name__ == '__main__':
	import requests

	url = "http://localhost:8194/wxLogin"

	params = {
		"params": utils.JsonEncode({  # 序列化的json字符串
			'uid': 1001,
			'name': "t",
			'imei': 123456,
			'mac': 0x12311,
			'errcode': 0,
			'code': "abccc",
			'unionid': "123456",
			'openid': "qwerty",
		}),
	}

	s = "params=" + urllib.parse.quote_plus(params["params"]) + "&key=2024CFD4-B5B1-4468-9ACE-60C3C6667B22"
	params["sign"] = utils.MD5(s)

	response = requests.get(url, params=params)

	# 检查响应状态码
	if response.status_code == 200:
		print("请求成功！")
		print("响应内容：", response.text)
	else:
		print("请求失败，状态码：", response.status_code)
