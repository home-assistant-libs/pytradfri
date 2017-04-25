from setuptools import setup

VERSION = 1.1
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

setup(
  name='pytradfri',
  packages=['pytradfri'],
  version=VERSION,
  description='A python library for communicating with the Tradfri Gateway',
  author='balloob, ggravlingen',
  author_email='no@email.com',
  url='https://github.com/ggravlingen/pytradfri',
  download_url=DOWNLOAD_URL
)
