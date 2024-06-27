# -*- coding: utf-8 -*-
import json
import time
import urllib.parse

from utils import utils

if __name__ == '__main__':
	import requests

	for i in range(10):
		params = json.dumps({
			'code':"12321321",
		})

		url = f"http://127.0.0.1:8194/server/WxPayOrderPush?params={params}&sign=65005ba49d76c6fc15d51d24b101df3c&nonce=432423adsa&timestamp=1718963302"

		response = requests.post(url)

		# 检查响应状态码
		if response.status_code == 200:
			print("请求成功！")
			print("响应内容：", response.text)
		else:
			print("请求失败，状态码：", response.status_code)
