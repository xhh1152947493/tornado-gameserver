# -*- coding: utf-8 -*-

import signal

import tornado.ioloop
import tornado.httpserver
import tornado.web

from configs import config
from utils.log import Log
from tornado.options import define, options

from controllers.login import CWxLoginHandler, CGuestLoginHandler, CAutoTokenLoginHandler
from controllers.pay import CWxPayRetPushHandler, CWxPayRewardReqHandler, CWxPayOrderQueryHandler, \
	CWxPayOrderCreateHandler
from controllers.game import CUploadUserDataHandler


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			("/guestLogin", CGuestLoginHandler),
			("/autoTokenLogin", CAutoTokenLoginHandler),
			("/wxLogin", CWxLoginHandler),
			("/wxPayOrderCreate", CWxPayOrderCreateHandler),
			("/wxPayRetPush", CWxPayRetPushHandler),
			("/wxPayOrderQuery", CWxPayOrderQueryHandler),
			("/wxPayRewardReq", CWxPayRewardReqHandler),
			("/uploadUserData", CUploadUserDataHandler),
		]

		settings = dict(
			xsrf_cookies=False,
			debug=config.IS_DEBUG,
			xheaders=True,
		)

		tornado.web.Application.__init__(self, handlers, **settings)


server = None  # Web Server 实例


def _signal(*sig):
	for s in sig:
		signal.signal(s, sig_handler)
		Log.info('register signal:%s', s)


def sig_handler(sig, frame):
	"""立即打断主线程正在执行的逻辑，函数结束后返回继续执行"""
	Log.warning('caught signal:%s', sig)
	tornado.ioloop.IOLoop.instance().add_callback_from_signal(shutdown)


def shutdown():
	Log.warning('stopping http server')
	server.stop()  # 拒绝新请求

	Log.warning('will shutdown in %s seconds...', config.SHUTDOWN_WAIT_SECONDS)
	io_loop = tornado.ioloop.IOLoop.instance()

	def final_shutdown():
		io_loop.stop()
		Log.warning('shutdown complete')

	# 关闭进程前确保剩余消息都执行完了
	io_loop.call_later(config.SHUTDOWN_WAIT_SECONDS, final_shutdown)


define("port", default=8194, help="web server run on the given port", type=int)


def bootstrap():
	global server

	tornado.options.parse_command_line()  # 解析命令行参数

	server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
	server.listen(options.port)

	Log.info('webserver start on port:%d, is_debug:%s', options.port, config.IS_DEBUG)

	_signal(signal.SIGTERM, signal.SIGINT)  # kill -SIGTERM 1234 [kill -9不触发此信号] | ctrl + c

	tornado.ioloop.IOLoop.instance().start()  # 启动事件循环,阻塞

	Log.warning('webserver exit')


# 启动命令：nohup python3 web_server.py --port=8194 &
if __name__ == "__main__":
	bootstrap()
