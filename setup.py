#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = "5.6.0"
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

EXTRAS_REQUIRE = {
    'async': ['aiocoap >= 0.4a1', 'DTLSSocket >= 0.1.4']
}

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

setup(
  name='pytradfri',
  packages=PACKAGES,
  python_requires='>=3.4',
  version=VERSION,
  description='IKEA Trådfri/Tradfri API. Control and observe your '
              'lights from Python.',
  long_description=long_description,
  author='balloob, lwis, ggravlingen',
  author_email='no@email.com',
  url='https://github.com/ggravlingen/pytradfri',
  license='MIT',
  keywords='ikea tradfri api iot light homeautomation',
  download_url=DOWNLOAD_URL,
  extras_require=EXTRAS_REQUIRE,
)
