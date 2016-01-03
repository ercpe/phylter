# -*- coding: utf-8 -*-
import re
from phylter.backends.base import Backend
from phylter.conditions import Condition, OrOperator, AndOperator, EqualsCondition, \
	GreaterThanOrEqualCondition, LessThanCondition, LessThanOrEqualCondition, GreaterThanCondition

number_re = re.compile("^-?\d+(\.\d+)?$")

def digit_or_float(s):
	return s.isdigit() or number_re.match(s) is not None

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
			left_value = self.get_item_value(item, op.left)
			right_value = self.get_item_value(item, op.right)

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

	def get_item_value(self, item, name_or_value):
		if isinstance(name_or_value, (int, float)) or digit_or_float(name_or_value):
			return float(name_or_value)

		if name_or_value[0] in ("'", '"') and name_or_value[0] == name_or_value[-1]:
			# quoted string
			return name_or_value[1:-1]

		return getattr(item, name_or_value)
