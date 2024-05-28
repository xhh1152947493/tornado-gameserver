# -*- coding: utf-8 -*-

# */5 * * * * python3 backup.py
def backup():
	"""
	数据备份，每5分钟执行一次
	1.备份最新mysql数据
	2.读取redis数据，并上传oss对象存储
	"""


if __name__ == '__main__':
	backup()
