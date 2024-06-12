# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers

from configs import config
from defs import const

_main_log_name = "__main__"
_main_file_name = "main.log"
_max_bytes = 1024 * 1024 * 5  # 5MB,设置单个文件大小
_backup_count = 200  # 最大备份日志数量
_format = '%(asctime)-15s %(levelname)s %(message)s'

log = logging.getLogger(_main_log_name)


def _init_logger():
	"""log是在当前线程写入的,设置日志文件大小避免写入log时阻塞当前线程"""
	global log

	if not os.path.exists(const.LOG_PATH):
		os.makedirs(const.LOG_PATH)

	# 实例化handler
	handler = logging.handlers.RotatingFileHandler(const.LOG_PATH + _main_file_name, mode="aw+", maxBytes=_max_bytes,
	                                               backupCount=_backup_count, encoding="utf-8")
	formatter = logging.Formatter(_format)  # 实例化formatter
	handler.setFormatter(formatter)  # 为handler添加formatter

	log.addHandler(handler)
	log.setLevel(config.get_log_level())  # 设置可记录的日志等级

	# 设置tornado的控制台输出也到log中
	tornado_logger = logging.getLogger("tornado")
	tornado_logger.addHandler(handler)
	tornado_logger.setLevel(config.get_log_level())


_init_logger()
