# -*- coding: utf-8 -*-
import pytest

from phylter.conditions import EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, LessThanCondition, \
	LessThanOrEqualCondition
from phylter.parser import ConsumableIter, Parser


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

	def test_parse(self):
		for query, left, right, clazz in (
			('foo == bar', 'foo', 'bar', EqualsCondition),
			('foo > bar', 'foo', 'bar', GreaterThanCondition),
			('foo < bar', 'foo', 'bar', LessThanCondition),
			('foo >= bar', 'foo', 'bar', GreaterThanOrEqualCondition),
			('foo <= bar', 'foo', 'bar', LessThanOrEqualCondition),
		):
			q = Parser().parse(query)
			assert len(q) == 1
			assert isinstance(q[0], clazz)
			assert q[0].left == left
			assert q[0].right == right
