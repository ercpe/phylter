# -*- coding: utf-8 -*-
import pyparsing

from phylter.conditions import EqualsCondition, GreaterThanCondition, LessThanCondition, GreaterThanOrEqualCondition, \
	LessThanOrEqualCondition

field = pyparsing.Word(pyparsing.alphanums)
operator = pyparsing.oneOf(('==', '!=', '>', '<', '>=', '<='))
value = pyparsing.quotedString | pyparsing.Word(pyparsing.alphanums)

#and_or = pyparsing.oneOf(['and', 'or'], caseless=True)

field_op_value = field + operator + value

#andor_field_op_value = and_or + field_op_value

pattern = field_op_value #+ pyparsing.Optional(pyparsing.OneOrMore(andor_field_op_value))


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


class Parser(object):

	def __init__(self, *args, **kwargs):
		pass

	def parse(self, query):
		chunks = ConsumableIter(pattern.parseString(query, parseAll=True))

		while chunks.has_more:
			left, operator, right = tuple(chunks.consume(3))
			return [self._get_condition_class(operator)(left, right)]

	def _get_condition_class(self, operator):
		d = {
			'==': EqualsCondition,
			'>': GreaterThanCondition,
			'<': LessThanCondition,
			'>=': GreaterThanOrEqualCondition,
			'<=': LessThanOrEqualCondition
		}
		if not operator in d:
			raise Exception("Unknown operator '%s'" % operator)
		return d[operator]