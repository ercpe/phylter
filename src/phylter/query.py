# -*- coding: utf-8 -*-

class Query(object):

	def __init__(self, q):
		self.query = q

	def __str__(self):  # pragma: nocover
		return ' '.join([str(x) for x in self.query])

	def __repr__(self):  # pragma: nocover
		return "%s(%s)" % (self.__class__.__name__, self.__str__())