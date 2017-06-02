from setuptools import setup

VERSION = 2.0
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

AIO_REQUIRES = [
    'async_timeout',
    "https://github.com/chrysn/aiocoap/archive/2d2142043d6c8c8b81b22ca0cdf5e1695361a02c.zip#aiocoap==0.3"  # tinydtls branch.
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
  extras_require={'asyncio': AIO_REQUIRES},
)
