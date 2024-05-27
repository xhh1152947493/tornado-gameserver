# -*- coding: utf-8 -*-

import signal

import tornado.ioloop
import tornado.httpserver
import tornado.web

from configs import config
from utils.log import logger
from tornado.options import define, options

from controllers import login_handlers


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			("/wechatLogin", login_handlers.WeChatLoginHandler),
		]

		settings = dict(
			xsrf_cookies=False,
			debug=config.IS_DEBUG,
			xheaders=True,
		)

		tornado.web.Application.__init__(self, handlers, **settings)


server = None  # Web Server 实例


def sig_handler(sig, frame):
	logger.warning('Caught signal: %s', sig)
	tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
	logger.info('Stopping HTTP server')
	server.stop()

	logger.info('Will shutdown in %s seconds...', config.SHUTDOWN_WAIT_SECONDS)
	io_loop = tornado.ioloop.IOLoop.instance()

	def final_shutdown():
		io_loop.stop()
		logger.info('Shutdown complete')

	# 关闭进程前确保剩余消息都执行完了
	io_loop.call_later(config.SHUTDOWN_WAIT_SECONDS, final_shutdown)


define("port", default=8194, help="web server run on the given port", type=int)


def main():
	global server

	tornado.options.parse_command_line()  # 解析命令行参数

	server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
	server.listen(options.port)

	logger.info('webserver start on port:%d, is_debug:%s', options.port, config.IS_DEBUG)

	signal.signal(signal.SIGTERM, sig_handler)  # kill -SIGTERM 1234 [kill -9不触发此信号]
	signal.signal(signal.SIGINT, sig_handler)  # ctrl + c

	tornado.ioloop.IOLoop.instance().start()  # 启动事件循环,阻塞

	logger.info('webserver exit')


# 启动命令：nohup python3 main.py --port=8194 &
if __name__ == "__main__":
	main()
