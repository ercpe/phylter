# -*- coding: utf-8 -*-

class Condition(object):

	def __init__(self, left, right):
		self.left = left
		self.right = right


class EqualsCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s == %s" % (self.left, self.right)


class GreaterThanCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s > %s" % (self.left, self.right)


class GreaterThanOrEqualCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s >= %s" % (self.left, self.right)


class LessThanCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s < %s" % (self.left, self.right)


class LessThanOrEqualCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s <= %s" % (self.left, self.right)


class Operator(object):
	def __init__(self, left, right):
		self.left = left
		self.right = right


class AndOperator(Operator):
	pass

class OrOperator(Operator):
	pass

