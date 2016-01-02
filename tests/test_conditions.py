# -*- coding: utf-8 -*-
from phylter.conditions import EqualsCondition, GreaterThanCondition, AndOperator, OrOperator


class TestConditions(object):

	def test_equals(self):
		assert EqualsCondition('foo', 'bar') == EqualsCondition('foo', 'bar')
		assert EqualsCondition('foo', 'bar') != GreaterThanCondition('foo', 'bar')


class TestOperators(object):

	def test_equals(self):
		assert AndOperator('foo', 'bar') == AndOperator('foo', 'bar')
		assert AndOperator('foo', 'bar') != OrOperator('foo', 'bar')
