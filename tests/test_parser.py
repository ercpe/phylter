# -*- coding: utf-8 -*-
import pytest
from pyparsing import ParseException

from phylter.conditions import EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, LessThanCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator, ConditionGroup
from phylter.parser import ConsumableIter, Parser, pattern
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

	def test_current_and_next(self):
		ci = ConsumableIter([1, 2, 3])
		assert ci.current == 1
		assert ci.next == 2

	def test_current_and_next_empty(self):
		ci = ConsumableIter([])
		assert ci.current is None
		assert ci.next is None

	def test_current_and_next_beyond_end(self):
		ci = ConsumableIter([1])
		ci.consume()
		assert ci.current is None
		assert ci.next is None

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
			print("------")

	def test_parse_groups(self):
		s = "foo == 'bar' or (foo == 'baz' or foo=='bat')"
		q = Parser().parse(s)
		assert q.query.iterable == [
			OrOperator(
				EqualsCondition('foo', "'bar'"),
				ConditionGroup(
					OrOperator(
							EqualsCondition('foo', "'baz'"),
							EqualsCondition('foo', "'bat'")
					)
				)
			)
		]

		# multiple group
		s = "foo == 'bar' or (foo == 'baz' or foo=='bat') or (a == 1 and b < 2)"
		q = Parser().parse(s)
		assert q.query.iterable == [
			OrOperator(
				OrOperator(
					EqualsCondition('foo', "'bar'"),
					ConditionGroup(
						OrOperator(
								EqualsCondition('foo', "'baz'"),
								EqualsCondition('foo', "'bat'")
						)
					)
				),
				ConditionGroup(
					AndOperator(
						EqualsCondition('a', '1'),
						LessThanCondition('b', '2'),
					)
				)
			)
		]

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
		):
			with pytest.raises(ParseException) as e:
				Parser().parse(s)

	def test_find_group_end(self):
		p = Parser()

		for items, group_end_pos in (
			(['foo', '==', '1', ')'], 3),
			(['foo', '==', '1', ')', 'or', 'a', '==', '1'], 3),
			(['foo', '==', '1', ')', 'or', '(', 'foo', '==', '1', ')'], 3),
		):
			assert p.find_group_end(ConsumableIter(items)) == group_end_pos

		with pytest.raises(Exception):
			assert p.find_group_end(ConsumableIter(['foo', '==', 'bar'])) == group_end_pos

		with pytest.raises(Exception) as e:
			assert p.find_group_end(ConsumableIter(['(', 'foo', '==', 'bar'])) == group_end_pos
