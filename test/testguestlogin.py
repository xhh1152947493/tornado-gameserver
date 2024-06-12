# -*- coding: utf-8 -*-
import string
import random
import time

from utils import utils


def generate_random_string(length):
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for _ in range(length))


random_string = generate_random_string(11)

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


# 加密函数
def encryptAES(plaintext, key):
	encrypted = b''
	for c in plaintext.encode('utf-8'):
		c += 1
		c ^= key
		encrypted += bytes(c)

	rlt = base64.b64encode(encrypted).decode('utf-8')
	return rlt


def encrypt(plaintext, http_encrypt_key):
	# 将明文字符串转换为字节数组
	plaintext_bytes = plaintext.encode()

	ciphertext = bytearray()

	# 遍历明文字节
	for plaintext_byte in plaintext_bytes:
		# 对每个字节执行与 HTTP 加密密钥的异或操作，并减一
		plaintext_byte += 1
		n = plaintext_byte ^ http_encrypt_key
		ciphertext.append(n)

	rlt = base64.b64encode(ciphertext).decode('utf-8')
	return rlt


if __name__ == '__main__':
	import requests

	url = "http://localhost:8194/guestLogin"

	# params = {
	# 	"params": "dasdas", # 非法json
	# }

	params = {
		"params": encrypt(utils.json_encode({  # 序列化的json字符串
			'imei': "YQyNXaFlx2F",
		}), 0x5a),
	}

	response = requests.get(url, params=params)

# # 创建一个Session对象
# session = requests.Session()
#
# # 设置一些默认的headers
# session.headers.update({'User-Agent': 'my-app/0.0.1'})
# session.headers.update({
# 	'JwtToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IiIsImV4cCI6MTcxNzY3MTQ2Mn0.KSas5Wxj8sg_HYzuWFZC6YTgkfMtErtSJyrlJbB0vMQ'})
#
# while True:
#
# 	params = {
# 		"params": encryptAES(utils.json_encode({  # 序列化的json字符串
# 			'imei': generate_random_string(11),
# 		}), b'9Lx6Kl6dh5b8/gpXPlfRXg=='),
# 	}
#
# 	response = session.get(url, params=params)
#
# 	# 检查响应状态码
# 	if response.status_code == 200:
# 		print(f"请求成功！ 响应内容：{response.text}")
# 	else:
# 		print(f"请求失败！状态码:{response.status_code} 响应内容：{response.text}")

# time.sleep(3)

# for i in range(50):
# 	params = {
# 		"params": utils.json_encode({  # 序列化的json字符串
# 			'imei': generate_random_string(11),
# 		}),
# 	}
#
# 	response = session.get(url, params=params)
#
# 	# 检查响应状态码
# 	if response.status_code == 200:
# 		print(f"请求成功！ 响应内容：{response.text}")
# 	else:
# 		print(f"请求失败！状态码:{response.status_code} 响应内容：{response.text}")
#
# time.sleep(3)
#
# for i in range(10):
# 	params = {
# 		"params": utils.json_encode({  # 序列化的json字符串
# 			'imei': generate_random_string(11),
# 		}),
# 	}
#
# 	response = session.get(url, params=params)
#
# 	# 检查响应状态码
# 	if response.status_code == 200:
# 		print(f"请求成功！ 响应内容：{response.text}")
# 	else:
# 		print(f"请求失败！状态码:{response.status_code} 响应内容：{response.text}")
