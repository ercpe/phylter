# -*- coding: utf-8 -*-
import pytest
import sys
from django.db.models import Q
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from phylter.backends import backends, get_backend
from phylter.backends.base import Backend, str_types
from phylter.backends.django_backend import DjangoBackend
from phylter.backends.objects import ObjectsBackend
from phylter.conditions import EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, LessThanCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator
from phylter.query import Query


class TestBackends(object):

	def test_objectbackend_exists(self):
		assert ObjectsBackend in backends
		assert DjangoBackend in backends

	def test_get_backend(self):
		class Foo(object):
			pass

		be = get_backend(Foo())
		assert isinstance(be, ObjectsBackend)

	@pytest.mark.skipif(sys.version_info >= (3, 0), reason="requires python 2")
	def test_str_types_py2(self):
		assert str_types == (str, unicode, bytes)

	@pytest.mark.skipif(sys.version_info < (3, 0), reason="requires python 3")
	def test_str_types_py3(self):
		assert str_types == (str, bytes)

	def test_get_compatible_value(self):
		ob = Backend()

		assert ob.get_compatible_value('"test"') == "test"
		assert ob.get_compatible_value(10) == 10
		assert ob.get_compatible_value("10", int) == 10
		assert ob.get_compatible_value("10.0", int) == 10
		assert ob.get_compatible_value("10.0", float) == 10
		assert ob.get_compatible_value("-10", int) == -10
		assert ob.get_compatible_value("-10.0", int) == -10
		assert ob.get_compatible_value("-10.0", float) == -10

		assert ob.get_compatible_value(True) == True


class TestObjectBackend(object):

	def test_supports(self):
		class Foo(object):
			pass

		assert ObjectsBackend.supports(1)
		assert ObjectsBackend.supports(True)
		assert ObjectsBackend.supports(Foo())

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


class TestDjangoBackend(object):

	def test_supports(self):
		assert DjangoBackend.supports(QuerySet())
		assert DjangoBackend.supports(Manager())
		assert not DjangoBackend.supports(Q())

	def test_get_backend(self):
		assert isinstance(get_backend(QuerySet()), DjangoBackend)
		assert isinstance(get_backend(Manager()), DjangoBackend)

	def test_to_q(self):
		db = DjangoBackend()

		assert db.to_q(EqualsCondition('a', 1)).children == [('a', 1)]
		assert db.to_q(GreaterThanCondition('a', 0)).children == [('a__gt', 0)]
		assert db.to_q(GreaterThanOrEqualCondition('a', 1)).children == [('a__gte', 1)]
		assert db.to_q(LessThanCondition('a', 2)).children == [('a__lt', 2)]
		assert db.to_q(LessThanOrEqualCondition('a', 1)).children == [('a__lte', 1)]

		q = db.to_q(AndOperator(EqualsCondition('a', 1), GreaterThanCondition('a', 0)))
		assert len(q.children) == 2
		assert q.children[0].children == [('a', 1)]
		assert q.children[1].children == [('a__gt', 0)]
		assert q.connector == 'AND'

		q = db.to_q(OrOperator(EqualsCondition('a', 1), GreaterThanCondition('a', 0)))
		assert len(q.children) == 2
		assert q.children[0].children == [('a', 1)]
		assert q.children[1].children == [('a__gt', 0)]
		assert q.connector == 'OR'
