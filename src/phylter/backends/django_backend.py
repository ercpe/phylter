# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from phylter.backends.base import Backend
from phylter.conditions import Condition, EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, \
	LessThanCondition, LessThanOrEqualCondition, AndOperator, OrOperator


class DjangoBackend(Backend):

	@staticmethod
	def supports(o):
		return isinstance(o, QuerySet) or isinstance(o, Manager)

	def apply(self, query, iterable):
		django_query = iterable if isinstance(iterable, QuerySet) else iterable.all()

		for o in query.query:
			django_query = self.apply_django_filter(django_query, o)

		return django_query

	def apply_django_filter(self, django_query, obj):
		return django_query.filter(self.to_q(obj))

	def to_q(self, obj):
		if isinstance(obj, Condition):
			suffix = {
				EqualsCondition: "",
				GreaterThanCondition: "__gt",
				GreaterThanOrEqualCondition: "__gte",
				LessThanCondition: "__lt",
				LessThanOrEqualCondition: "__lte",
			}[obj.__class__]

			f = "%s%s" % (obj.left, suffix)
			return Q(**{f: self.get_compatible_value(obj.right)})

		if isinstance(obj, AndOperator):
			return Q(self.to_q(obj.left), self.to_q(obj.right))

		if isinstance(obj, OrOperator):
			return Q(self.to_q(obj.left)) | Q(self.to_q(obj.right))

		raise Exception("Unexpected item found in query: %s" % obj)
