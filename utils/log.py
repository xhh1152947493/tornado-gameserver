# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers

from configs import config, const

_main_log_name = "__main__"
_main_file_name = "main.log"
_max_bytes = 1024 * 1024 * 5
_back_up_count = 50
_format = '%(asctime)-15s %(levelname)s %(message)s'

logger = logging.getLogger(_main_log_name)


def _init_logger():
	"""log是在当前线程写入的,设置日志文件大小避免写入log时阻塞当前线程"""
	global logger

	if not os.path.exists(const.LOG_PATH):
		os.makedirs(const.LOG_PATH)

	# 实例化handler
	handler = logging.handlers.RotatingFileHandler(const.LOG_PATH + _main_file_name, mode="aw+",
	                                               maxBytes=_max_bytes, backupCount=_back_up_count)
	formatter = logging.Formatter(_format)  # 实例化formatter
	handler.setFormatter(formatter)  # 为handler添加formatter

	logger.addHandler(handler)
	logger.setLevel(config.get_log_level())  # 设置可记录的日志等级


_init_logger()
