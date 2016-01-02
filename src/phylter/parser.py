# -*- coding: utf-8 -*-
import pyparsing

from phylter.conditions import EqualsCondition, GreaterThanCondition, LessThanCondition, GreaterThanOrEqualCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator, Condition, Operator
from phylter.query import Query

field = pyparsing.Word(pyparsing.alphanums)
operator = pyparsing.oneOf(('==', '!=', '>', '<', '>=', '<='))
value = pyparsing.quotedString | pyparsing.Word(pyparsing.alphanums)

and_or = pyparsing.oneOf(['and', 'or'], caseless=True)

field_op_value = field + operator + value

andor_field_op_value = and_or + field_op_value

pattern = field_op_value + pyparsing.Optional(pyparsing.OneOrMore(andor_field_op_value))


class ConsumableIter(object):
	def __init__(self, iterable):
		self.iterable = iterable or []
		self.length = len(self.iterable)
		self.pos = 0

	@property
	def remaining(self):
		return self.length - self.pos

	@property
	def has_more(self):
		return self.remaining > 0

	@property
	def current(self):
		if self.pos >= self.length-1:
			return None

		return self.iterable[self.pos]

	def consume(self, length=1):
		if length is None or length < 0 or length > self.length:
			raise ValueError("'length' argument must be 0 <= length")

		if length > self.remaining:
			raise ValueError("Cannot consume more than %s remaining elements" % self.remaining)

		if length == 0:
			return None

		if length == 1:
			element = self.iterable[self.pos]
			self.pos += length
			return element

		elements = self.iterable[self.pos:self.pos+length]
		self.pos += length
		return elements

	def __len__(self):
		return self.length

	def __contains__(self, item):
		return item in self.iterable[self.pos:]

	def __getitem__(self, item):
		return ConsumableIter(self.iterable.__getitem__(item))

	def __iter__(self):
		return self.iterable.__iter__()

	def __eq__(self, other):
		return isinstance(other, ConsumableIter) and self.iterable[self.pos:] == other.iterable[other.pos:] or \
				isinstance(other, list) and self.iterable[self.pos:] == other

class Parser(object):

	def __init__(self, *args, **kwargs):
		pass

	def parse(self, query):
		chunks = ConsumableIter(pattern.parseString(query, parseAll=True))
		return self.build_query(chunks)

	def build_query(self, consumable):
		l = []

		# replace condition tuples with *Condition instances
		while consumable.has_more:
			left, operator, right = tuple(consumable.consume(3))
			condition = self._get_condition_class(operator)(left, right)
			l.append(condition)

			if consumable.has_more:
				l.append(consumable.consume())

		assert all((isinstance(x, Condition) or x in ('and', 'or') for x in l))

		l = ConsumableIter(l)
		# replace all operator with *Operator instances, from the lowest to the highest binding
		for op in ('or', 'and'):
			op_clazz = self._get_operator_class(op)
			l2 = []
			last = None

			while l.has_more:
				current = l.consume()

				if isinstance(current, Condition) or isinstance(current, Operator):
					last = current
				else:
					if current == op:
						last = op_clazz(last, l.consume())
					else:
						if last:
							l2.append(last)
							last = None
						l2.append(current)
			if last:
				l2.append(last)

			l = ConsumableIter(l2)

		return Query(l)

	def _get_condition_class(self, operator):
		d = {
			'==': EqualsCondition,
			'>': GreaterThanCondition,
			'<': LessThanCondition,
			'>=': GreaterThanOrEqualCondition,
			'<=': LessThanOrEqualCondition
		}
		if operator not in d:
			raise Exception("Unknown operator '%s'" % operator)
		return d[operator]

	def _get_operator_class(self, operator):
		d = {
			'and': AndOperator,
			'or': OrOperator
		}
		if operator.lower() not in d:
			raise Exception("Unknown operator '%s'" % operator)
		return d[operator]
