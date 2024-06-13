# -*- coding: utf-8 -*-

import tornado.web

from tornado.options import options
from data import error
from models import model
from .base_handler import CBaseHandler
from utils import utils, wx_crypt


def _checkSignature(sSign, sTimestamp, sNoce):
	tmpList = [options.wechatPayToken, sTimestamp, sNoce]
	tmpList.sort()

	sTmp = ''.join(tmpList)
	sTmp = utils.SHA1(sTmp)

	return sTmp == sSign


class CWxPayRetPushHandler(CBaseHandler):
	def prepare(self):
		pass

	def get(self):
		return self._request()

	def post(self):
		return self._request()

	def _request(self):
		if _checkSignature(self.GetString("signature"), self.GetString("timestamp"), self.GetString("nonce")):
			self.write(self.GetString("echostr"))
			self.finish()
		else:
			return self.write("check failed")
