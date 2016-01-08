# -*- coding: utf-8 -*-

class Condition(object):

	def __init__(self, left, right):
		self.left = left
		self.right = right

	def __eq__(self, other):
		return isinstance(other, self.__class__) and other.left == self.left and other.right == self.right

	def __repr__(self):
		return self.__str__()

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


class Operator(object):  # pragma: nocover
	def __init__(self, left, right):
		self.left = left
		self.right = right

	def __eq__(self, other):
		return isinstance(other, self.__class__) and other.left == self.left and other.right == self.right


class AndOperator(Operator):

	def __str__(self):  # pragma: nocover
		return "(%s) AND (%s)" % (self.left, self.right)


class OrOperator(Operator):

	def __str__(self):  # pragma: nocover
		return "(%s) OR (%s)" % (self.left, self.right)


class ConditionGroup(object):

	def __init__(self, item):
		self.item = item

	def __str__(self):
		return "(%s)" % self.item

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		return isinstance(other, ConditionGroup) and self.item == other.item