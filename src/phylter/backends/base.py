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
		if field_type in str_types or (field_type is None and isinstance(value, str_types)):
			s = value if isinstance(value, str_types) else str(value)

			if value[0] in ("'", '"') and value[0] == value[-1]:
				# quoted string
				return value[1:-1]

			return value

		if field_type in (int, float) or (field_type is None and isinstance(value, (int, float))):
			if isinstance(value, (int, float)):
				return value

			if isinstance(value, str_types) and digit_or_float(value):
				return float(value)

			return value

		return value