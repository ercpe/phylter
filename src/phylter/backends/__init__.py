# -*- coding: utf-8 -*-
from phylter.backends.objects import ObjectsBackend

backends = None

if backends is None:
	backends = []

	try:
		from phylter.backends.django_backend import DjangoBackend
		backends.append(DjangoBackend)
	except ImportError:
		pass

	backends.append(ObjectsBackend)


def get_backend(o):
	for b in backends:
		if b.supports(o):
			return b()

