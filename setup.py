#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION='0.2'

setup(
	name='phylter',
	version=VERSION,
	description='Library for a filter DSL in python',
	long_description=open('README.md').read(),
	author='Johann Schmitz',
	author_email='johann@j-schmitz.net',
	url='https://ercpe.de/projects/phylter',
	download_url='https://code.not-your-server.de/phylter.git/tags/%s.tar.gz' % VERSION,
	packages=find_packages('src'),
	package_dir={'': 'src'},
	include_package_data=True,
	zip_safe=False,
	license='GPL-3',
)
