# -*- coding: utf-8 -*-

# 服务端错误码列表：类型为short
OK = 0
ILLEGAL_PARAMS = 1  # 客户端请求数据错误，不符合即定格式
SYSTEM_ERR     = 2  # 系统错误[不好定义的错误都用这个返回]
DB_CONNECT_ERR = 3  # 数据库连接失败
DB_OPERATE_ERR = 4  # 数据库操作失败
DATA_NOT_FOUND = 5  # 数据丢失，找不到