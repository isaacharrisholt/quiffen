#!/usr/bin/env python

from setuptools import setup

setup(
    name='quiffen',
    version='1.0',
    description='Quiffen is a Python package for parsing QIF (Quicken Interchange Format) files.',
    author='Isaac Harris-Holt',
    author_email='isaac@harris-holt.com',
    url='https://github.com/isaacharrisholt/quiffen',
    packages=['quiffen', 'quiffen.core'],
)
