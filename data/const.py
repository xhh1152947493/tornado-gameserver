# -*- coding: utf-8 -*-
import os

# system running path.
ROOT_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'

# 日志文件写入路径
LOG_PATH = ROOT_PATH + 'output/logs/'

# 初始玩家id
INIT_GID = 100000

PAY_ORDER_STATE_IDLE = 0  # 已创建
PAY_ORDER_STATE_DONE = 1  # 已支付
PAY_ORDER_STATE_REWARDED = 2  # 已领奖
