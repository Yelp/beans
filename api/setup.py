# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name="yelp_beans",
    packages=find_packages(exclude=['tests*']),
)
