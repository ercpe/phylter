# -*- coding: utf-8 -*-
import pytest

from phylter.backends import backends, get_backend
from phylter.backends.objects import ObjectsBackend
from phylter.conditions import EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, LessThanCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator
from phylter.query import Query


class TestBackends(object):

	def test_objectbackend_exists(self):
		assert ObjectsBackend in backends

	def test_get_backend(self):
		class Foo(object):
			pass

		be = get_backend(Foo())
		assert isinstance(be, ObjectsBackend)

class TestObjectBackend(object):

	def test_supports(self):
		class Foo(object):
			pass

		assert ObjectsBackend.supports(1)
		assert ObjectsBackend.supports(True)
		assert ObjectsBackend.supports(Foo())

	def test_get_item_value(self):
		ob = ObjectsBackend()

		assert ob.get_item_value(None, '"test"') == "test"
		assert ob.get_item_value(None, "10") == 10
		assert ob.get_item_value(None, "10.0") == 10.0
		assert ob.get_item_value(None, "-10") == -10
		assert ob.get_item_value(None, "-10.0") == -10.0

		class Foo(object):
			def __init__(self):
				self.bar = 'baz'

		assert ob.get_item_value(Foo(), 'bar') == 'baz'

		with pytest.raises(AttributeError) as e:
			assert ob.get_item_value(Foo(), 'bat')

	def test_eval_op_condition(self):
		ob = ObjectsBackend()

		class Foo(object):
			a = 1

		assert ob.eval_op(EqualsCondition('a', 1), Foo())
		assert ob.eval_op(GreaterThanCondition('a', 0), Foo())
		assert ob.eval_op(GreaterThanOrEqualCondition('a', 1), Foo())
		assert ob.eval_op(LessThanCondition('a', 2), Foo())
		assert ob.eval_op(LessThanOrEqualCondition('a', 1), Foo())

	def test_eval_op_operator(self):
		ob = ObjectsBackend()

		class Foo(object):
			a = 1

		assert ob.eval_op(AndOperator(EqualsCondition('a', 1), GreaterThanCondition('a', 0)), Foo())
		assert ob.eval_op(OrOperator(EqualsCondition('a', 1), GreaterThanCondition('a', 0)), Foo())

		with pytest.raises(Exception):
			ob.eval_op(True, Foo())

	def test_apply(self):
		ob = ObjectsBackend()

		class Foo(object):
			a = 1

			def __eq__(self, other):
				return isinstance(other, Foo) and self.a == other.a

		query = Query([EqualsCondition('a', 1)])
		assert list(ob.apply(query, [Foo()])) == [Foo()]
		assert list(query.apply([Foo()])) == [Foo()]
