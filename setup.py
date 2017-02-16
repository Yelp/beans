# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

setup(
    name="yelp_beans",
    packages=find_packages(exclude=['tests*']),
)
