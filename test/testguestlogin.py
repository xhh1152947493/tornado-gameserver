# -*- coding: utf-8 -*-
import string
import random

from utils import utils


def generate_random_string(length):
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for _ in range(length))


random_string = generate_random_string(11)

if __name__ == '__main__':
	import requests

	url = "http://localhost:8194/guestLogin"

	for i in range(10):
		params = {
			"params": utils.json_encode({  # 序列化的json字符串
				'imei': generate_random_string(11),
			}),
		}

		response = requests.get(url, params=params)

		# 检查响应状态码
		if response.status_code == 200:
			print("请求成功！")
			print("响应内容：", response.text)
		else:
			print("请求失败，状态码：", response.status_code)
