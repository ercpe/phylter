# -*- coding: utf-8 -*-
import re
from phylter.backends.base import Backend
from phylter.conditions import Condition, OrOperator, AndOperator, EqualsCondition, \
	GreaterThanOrEqualCondition, LessThanCondition, LessThanOrEqualCondition, GreaterThanCondition


class ObjectsBackend(Backend):

	@staticmethod
	def supports(o):
		return True

	def apply(self, query, iterable):
		for item in iterable:
			if self.matches(query, item):
				yield item

	def matches(self, query, item):
		return all((self.eval_op(x, item) for x in query.query))

	def eval_op(self, op, item):
		if isinstance(op, Condition):
			left_value = getattr(item, op.left)
			right_value = self.get_compatible_value(op.right, type(left_value))

			return {
				EqualsCondition: lambda a, b: a == b,
				GreaterThanCondition: lambda a, b: a > b,
				GreaterThanOrEqualCondition: lambda a, b: a >= b,
				LessThanCondition: lambda a, b: a < b,
				LessThanOrEqualCondition: lambda a, b: a <= b,
			}[op.__class__](left_value, right_value)

		if isinstance(op, AndOperator):
			return self.eval_op(op.left, item) and self.eval_op(op.right, item)

		if isinstance(op, OrOperator):
			return self.eval_op(op.left, item) or self.eval_op(op.right, item)

		raise Exception("Unexpected item found in query: %s" % op)
