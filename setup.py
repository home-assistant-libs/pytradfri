from setuptools import setup, find_packages

VERSION = "4.0.1"
DOWNLOAD_URL = \
    'https://github.com/ggravlingen/pytradfri/archive/{}.zip'.format(VERSION)

EXTRAS_REQUIRE = {
    'async': ['aiocoap >= 0.3', 'DTLSSocket >= 0.1.4']
}

DEP_LINKS = [
    "https://github.com/chrysn/aiocoap/archive/3286f48f0b949901c8b5c04c0719dc54ab63d431.zip#egg=aiocoap-0.3"
]

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

setup(
  name='pytradfri',
  packages=PACKAGES,
  python_requires='>=3.4',
  version=VERSION,
  description='IKEA Trådfri/Tradfri API. Control and observe your '
              'lights from Python.',
  author='balloob, lwis, ggravlingen',
  author_email='no@email.com',
  url='https://github.com/ggravlingen/pytradfri',
  download_url=DOWNLOAD_URL,
  extras_require=EXTRAS_REQUIRE,
  dependency_links=DEP_LINKS,
)
