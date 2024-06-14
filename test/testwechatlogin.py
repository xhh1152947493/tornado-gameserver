# -*- coding: utf-8 -*-
import urllib.parse

from utils import utils

if __name__ == '__main__':
	import requests

	url = "http://localhost:8194/wxLogin"

	params = {
		'uid': "100002"
	}

	s = "uid=" + urllib.parse.quote_plus(params["uid"]) + "&key=2024CFD4-B5B1-4468-9ACE-60C3C6667B22" + "&token=oXeHPiPb3gIx79oZCpbYEJwUfz65YCTTqYVZcU5"
	params["sign"] = utils.MD5(s)

	response = requests.get(url, params=params)

	# 检查响应状态码
	if response.status_code == 200:
		print("请求成功！")
		print("响应内容：", response.text)
	else:
		print("请求失败，状态码：", response.status_code)
