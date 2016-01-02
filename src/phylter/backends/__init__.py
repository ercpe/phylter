# -*- coding: utf-8 -*-

from phylter.backends.objects import ObjectsBackend

backends = [
	ObjectsBackend
]

def get_backend(o):
	for b in backends:
		if b.supports(o):
			return b()

