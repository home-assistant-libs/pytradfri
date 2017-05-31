from setuptools import setup

VERSION = 2.0
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

REQUIRES = [
    'async_timeout',
    'aiocoap'
]

setup(
  name='pytradfri',
  packages=['pytradfri'],
  version=VERSION,
  description='A python library for communicating with the Tradfri Gateway',
  author='balloob, ggravlingen',
  author_email='no@email.com',
  url='https://github.com/ggravlingen/pytradfri',
  download_url=DOWNLOAD_URL,
  install_requires=REQUIRES,
)
