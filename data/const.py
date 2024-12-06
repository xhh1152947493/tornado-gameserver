# -*- coding: utf-8 -*-
import os

# system running path.
ROOT_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'

# 日志文件写入路径
LOG_PATH = ROOT_PATH + 'output/logs/'


INIT_GID      = 100000  # 初始玩家id
INIT_TRADE_ID = 47218677124323333895486091113873  # 初始订单id # Todo zhangzhihui 新开一个游戏是否有必要修改这个

PAY_ORDER_STATE_IDLE     = 0  # 已创建
PAY_ORDER_STATE_DONE     = 1  # 已支付
PAY_ORDER_STATE_REWARDED = 2  # 已领奖

COUNTER_ID_FOR_GID      = 1  # tbl_counter表中gid所在的id
COUNTER_ID_FOR_TRADE_ID = 2  # tbl_counter表中tradeID所在的id
