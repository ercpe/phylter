# -*- coding: utf-8 -*-
import pytest
from pyparsing import ParseException

from phylter.conditions import EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, LessThanCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator
from phylter.parser import ConsumableIter, Parser
from phylter.query import Query


class TestConsumableIter(object):

	def test_constructor(self):
		for v in (None, []):
			ci = ConsumableIter(v)
			assert ci.length == 0
			assert ci.remaining == 0

		ci = ConsumableIter([1, 2, 3])
		assert ci.length == 3
		assert ci.remaining == 3

	def test_current(self):
		ci = ConsumableIter([1, 2, 3])
		assert ci.current == 1

	def test_current_empty(self):
		ci = ConsumableIter([])
		assert ci.current is None

	def test_has_more(self):
		ci = ConsumableIter([1, 2, 3])
		assert ci.has_more

	def test_has_more_empty(self):
		ci = ConsumableIter([])
		assert not ci.has_more

	def test_consume(self):
		ci = ConsumableIter([1, 2, 3])
		with pytest.raises(ValueError):
			ci.consume(None)

		ci = ConsumableIter([1, 2, 3])
		with pytest.raises(ValueError):
			ci.consume(-1)

		ci = ConsumableIter([1, 2, 3])
		with pytest.raises(ValueError):
			ci.consume(100)

		ci = ConsumableIter([1, 2, 3])
		ci.consume(1)
		with pytest.raises(ValueError):
			ci.consume(3)

		ci = ConsumableIter([1, 2, 3])
		assert ci.consume(0) is None
		assert ci.consume(1) == 1
		assert ci.consume(1) == 2
		assert ci.consume(1) == 3
		assert ci.remaining == 0
		assert not ci.has_more

		ci = ConsumableIter([1, 2, 3])
		assert ci.consume(3) == [1, 2, 3]
		assert ci.remaining == 0
		assert not ci.has_more

	def test_consume_empty(self):
		ci = ConsumableIter([])

		with pytest.raises(ValueError):
			ci.consume(1)

	def test_slice(self):
		ci = ConsumableIter([1, 2, 3])
		part = ci[1:2]
		assert isinstance(part, ConsumableIter)
		assert part.iterable == [2]
		assert part.length == 1
		assert part.remaining == 1
		assert part.pos == 0

	def test_contains(self):
		ci = ConsumableIter([1, 2, 3, 4, 5])
		assert 1 in ci
		assert 5 in ci

		ci.consume()
		assert 1 not in ci # already consumed
		assert 5 in ci

	def test_len(self):
		ci = ConsumableIter([1, 2, 3])
		assert ci.length == 3
		assert len(ci) == 3

	def test_iter(self):
		ci = ConsumableIter([1, 2, 3])

		assert [x for x in ci] == [1, 2, 3]

class TestParser(object):

	def test_constructor(self):
		p = Parser()
		p = Parser('foo')
		p = Parser('foo', bar='baz')

	def test_get_condition_class(self):
		p = Parser()

		assert p._get_condition_class('==') == EqualsCondition
		assert p._get_condition_class('>') == GreaterThanCondition
		assert p._get_condition_class('<') == LessThanCondition
		assert p._get_condition_class('>=') == GreaterThanOrEqualCondition
		assert p._get_condition_class('<=') == LessThanOrEqualCondition

		for x in (None, 'foobar'):
			with pytest.raises(Exception) as e:
				p._get_condition_class(x)
				assert e

	def test_get_operator_class(self):
		p = Parser()

		assert p._get_operator_class('and') == AndOperator
		assert p._get_operator_class('or') == OrOperator

		for x in (None, 'foobar'):
			with pytest.raises(Exception) as e:
				p._get_operator_class(x)
				assert e

	def test_parse(self):
		for query, left, right, clazz in (
			('foo == bar', 'foo', 'bar', EqualsCondition),
			('foo > bar', 'foo', 'bar', GreaterThanCondition),
			('foo < bar', 'foo', 'bar', LessThanCondition),
			('foo >= bar', 'foo', 'bar', GreaterThanOrEqualCondition),
			('foo <= bar', 'foo', 'bar', LessThanOrEqualCondition),
		):
			q = Parser().parse(query).query
			assert q == ConsumableIter([
				clazz(left, right)
			])

	def test_parse_and_or(self):
		for query, result in (
			("a == 1 and b == 2 or c == 3", # a and (b or c)
				AndOperator(
					EqualsCondition('a', '1'),
					OrOperator(
						EqualsCondition('b', '2'),
						EqualsCondition('c', '3'),
					)
				)
			),
			("a == 1 or b == 2 and c == 3",  # (a or b) and c
				AndOperator(
					OrOperator(
						EqualsCondition('a', '1'),
						EqualsCondition('b', '2')
					),
					EqualsCondition('c', '3')
				)
			),
			("a == 1 or b == 2 or c == 3",
				OrOperator(
					OrOperator(
						EqualsCondition('a', '1'),
						EqualsCondition('b', '2')
					),
					EqualsCondition('c', '3')
				)
			),
			("a == 1 and b == 2 and c == 3",
				AndOperator(
					AndOperator(
						EqualsCondition('a', '1'),
						EqualsCondition('b', '2')
					),
					EqualsCondition('c', '3')
				)
			),
		):
			q = Parser().parse(query).query
			assert q == ConsumableIter([result])

	def test_parse_fail(self):
		for s in (
			'foo == ',
			'foo == 1 and ',
			'foo == 1 or ',
			'or',
			'and',
			'foo == bar and (foo < 1 or foo > 2)',
		):
			with pytest.raises(ParseException) as e:
				Parser().parse(s)
