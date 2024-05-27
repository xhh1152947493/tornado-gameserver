# -*- coding: utf-8 -*-
from utils import utils

if __name__ == '__main__':
	import requests

	url = "http://localhost:8194/wechatLogin"

	params = {
		"params": utils.json_encode({  # 序列化的json字符串
			'uid': 1001,
			'name': "t",
			'imei': 123456,
			'mac': 0x12311,
		}),
	}

	response = requests.get(url, params=params)

	# 检查响应状态码
	if response.status_code == 200:
		print("请求成功！")
		print("响应内容：", response.text)
	else:
		print("请求失败，状态码：", response.status_code)
