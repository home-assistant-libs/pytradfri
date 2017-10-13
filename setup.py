from setuptools import setup, find_packages

VERSION = "2.2.3"
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

EXTRAS_REQUIRE = {
    'async': ['aiocoap >= 0.3']
}

DEP_LINKS = [
    "https://github.com/chrysn/aiocoap/archive/0df6a1e44582de99ae944b6a7536d08e2a612e8f.zip#egg=aiocoap-0.3"
]

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

setup(
  name='pytradfri',
  packages=PACKAGES,
  python_requires='>=3.4',
  version=VERSION,
  description='A Python library for communicating with the Tradfri Gateway',
  author='balloob, ggravlingen, lwis',
  author_email='no@email.com',
  url='https://github.com/ggravlingen/pytradfri',
  download_url=DOWNLOAD_URL,
  extras_require=EXTRAS_REQUIRE,
  dependency_links=DEP_LINKS,
)
