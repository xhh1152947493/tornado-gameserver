# -*- coding: utf-8 -*-

import subprocess

from configs import const
from models import db_sql, table_name, redis_keys, db_redis
from utils import utils


# */5 * * * * python3 backup.py
def backup():
	"""
	数据备份，每5分钟执行一次
	1.备份最新mysql数据
	2.读取redis数据，并上传oss对象存储
	"""

	# 定义命令和参数
	command = [
		'mysqldump',
		'-uroot',
		'-phr@123-zzh',
		'game',
		'tbl_user'
	]

	# 定义输出文件
	output_file = const.ROOT_PATH + 'sql/backup.sql'
	output_log = '/scripts/backup.log'

	# # 打开输出文件
	# with open(output_file, 'w') as f:
	# 	# 执行命令并将输出写入文件
	# 	result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)
	#
	# if result.returncode == 0:
	# 	utils.log(output_log, "Mysql backup successful.")
	# else:
	# 	utils.log(output_log, "Mysql backup failed. Error:{0}".format(result.stderr))

	conn = db_sql.connect("db_sql")
	if not conn:
		utils.log(output_log, "Mysql Connect failed")
		return

	conn_redis = db_redis.share_connect()
	if not conn_redis:
		utils.log(output_log, "Redis Connect failed")
		return

	rows = conn.query("SELECT `uid` FROM `{0}`".format(table_name.TABLE_USER))
	for row in rows:
		uid = row.get("uid")
		if not uid:
			continue
		bs = conn_redis.get(redis_keys.keys_player_game(uid))
		if not bs:
			utils.log(output_log, "uid:{0} has not redis data.".format(uid))
			continue
		# Todo zhangzhihui 上传oss


if __name__ == '__main__':
	backup()
