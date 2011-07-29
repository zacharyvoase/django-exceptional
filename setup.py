#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_version():
    data = read_from(rel_file('src', 'djexceptional', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)


setup(
    name             = 'django-exceptional',
    version          = get_version(),
    author           = "Zachary Voase",
    author_email     = "z@zacharyvoase.com",
    url              = 'http://github.com/zacharyvoase/django-exceptional',
    description      = "A Django client for Exceptional (getexceptional.com).",
    packages         = ['djexceptional', 'djexceptional.tests'],
    package_dir      = {'': 'src'},
)
