/*
 Navicat Premium Data Transfer

 Source Server         : 本地虚拟机
 Source Server Type    : MySQL
 Source Server Version : 50742
 Source Host           : 192.168.190.129:3306
 Source Schema         : game

 Target Server Type    : MySQL
 Target Server Version : 50742
 File Encoding         : 65001

 Date: 14/06/2024 17:29:36
*/


CREATE DATABASE game CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE game;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tbl_counter
-- ----------------------------
DROP TABLE IF EXISTS `tbl_counter`;
CREATE TABLE `tbl_counter`  (
  `id` int(4) NOT NULL,
  `counter_value` int(10) NOT NULL DEFAULT 0 COMMENT '账号创建次数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tbl_online
-- ----------------------------
DROP TABLE IF EXISTS `tbl_online`;
CREATE TABLE `tbl_online`  (
  `uid` int(11) NOT NULL COMMENT '用户id',
  `login_time` int(10) NULL DEFAULT NULL COMMENT '登录时间',
  `token` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '会话密钥\r\n',
  `session_key` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '会话密钥\r\n',
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tbl_order
-- ----------------------------
DROP TABLE IF EXISTS `tbl_order`;
CREATE TABLE `tbl_order`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `trade_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '订单号\r\n',
  `open_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户唯一标识',
  `create_timestamp` int(11) NULL DEFAULT NULL COMMENT '订单创建时间',
  `success_timestamp` int(11) NULL DEFAULT NULL COMMENT '订单支付成功时间',
  `event` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '事件类型\r\n',
  `env` int(4) NULL DEFAULT NULL COMMENT '环境配置\r\n0：现网环境（也叫正式环境）\r\n1：沙箱环境',
  `product_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '游戏道具id标识\r\n',
  `quantity` int(10) NULL DEFAULT NULL COMMENT '购买道具数量\r\n',
  `zone_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '分区ID\r\n',
  `orig_price` int(10) NULL DEFAULT NULL COMMENT '物品原始价格 （单位：分）\r\n',
  `actual_price` int(10) NULL DEFAULT NULL COMMENT '物品实际支付价格（单位：分）\r\n',
  `attach` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '透传数据\r\n',
  `order_source` int(4) NULL DEFAULT NULL COMMENT '1 游戏内 2 商城下单 3 商城测试下单\r\n',
  `mch_order_no` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '微信支付商户单号\r\n',
  `trans_action_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '交易单号(微信支付单号)\r\n',
  `to_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '小游戏原始ID\r\n',
  `from_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '该事件消息的openid，道具发货场景固定为微信官方的openid',
  `is_mock` int(1) NULL DEFAULT NULL COMMENT 'True: 模拟测试推送  False：真实推送\r\n',
  `state` int(1) NOT NULL DEFAULT 0 COMMENT '0：已生成\r\n1：已支付\r\n2：已发奖',
  PRIMARY KEY (`id`, `trade_id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE,
  UNIQUE INDEX `trade_id`(`trade_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tbl_switch
-- ----------------------------
DROP TABLE IF EXISTS `tbl_switch`;
CREATE TABLE `tbl_switch`  (
  `choice_env` int(1) NULL DEFAULT 0 COMMENT '支付环境,0正式环境,1测试沙箱环境'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tbl_user
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user`;
CREATE TABLE `tbl_user`  (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `imei` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `mac` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `auto_token` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '服务器生成的唯一值,可根据这个值直接登录',
  `open_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户唯一标识',
  `union_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户在开放平台的唯一标识符，若当前小程序已绑定到微信开放平台账号下会返回',
  `data` blob NULL COMMENT '玩家数据,最大64kb',
  PRIMARY KEY (`uid`, `open_id`, `union_id`) USING BTREE,
  UNIQUE INDEX `uid`(`uid`) USING BTREE,
  UNIQUE INDEX `open_id`(`open_id`) USING BTREE,
  UNIQUE INDEX `union_id`(`union_id`) USING BTREE,
  UNIQUE INDEX `auto_token`(`auto_token`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100021 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
