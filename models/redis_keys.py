# -*- coding: utf-8 -*-

# 递增的玩家id
def keys_guid():
	return "incr_guid"


# 玩家游戏数据
def keys_player_game(pid):
	return f"player_game_info:{pid}"
