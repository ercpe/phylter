# -*- coding: utf-8 -*-

class Backend(object): # pragma: nocover

	@staticmethod
	def supports(o):
		raise NotImplementedError

	def apply(self, query, iterable):
		raise NotImplementedError
