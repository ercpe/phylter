# -*- coding: utf-8 -*-
import re
import sys

number_re = re.compile("^-?\d+(\.\d+)?$")

def digit_or_float(s):
	return s.isdigit() or number_re.match(s) is not None

if sys.version_info[0] == 2:
	str_types = (str, unicode, bytes)
else:
	str_types = (str, bytes)


class Backend(object):

	@staticmethod
	def supports(o):  # pragma: nocover
		raise NotImplementedError

	def apply(self, query, iterable):  # pragma: nocover
		raise NotImplementedError

	def get_compatible_value(self, value, field_type=None):
		if value is None:
			return None

		value_type = type(value)

		if field_type and value_type == field_type:
			return value

		if field_type in str_types or (field_type is None and value_type in str_types):
			s = value if isinstance(value, str_types) else str(value)

			if s[0] in ("'", '"') and s[0] == s[-1]:
				# quoted string
				return s[1:-1]

			return value

		if field_type in (int, float) or (field_type is None and value_type in (int, float)):
			if value_type in (int, float):
				return value

			if value_type in str_types and digit_or_float(value):
				return float(value)

			return value

		return value