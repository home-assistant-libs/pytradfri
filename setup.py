#!/usr/bin/env python3
"""Set up pytradfri."""
from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")

VERSION = (PROJECT_DIR / "pytradfri" / "VERSION").read_text().strip()

GITHUB_URL = "https://github.com/home-assistant-libs/pytradfri"
DOWNLOAD_URL = f"{GITHUB_URL}/archive/{VERSION}.zip"

EXTRAS_REQUIRE = {"async": ["aiocoap~=0.4.5", "DTLSSocket~=0.1.12"]}
INSTALL_REQUIRES = ["pydantic"]
PACKAGES = find_packages(exclude=["tests", "tests.*"])

setup(
    name="pytradfri",
    packages=PACKAGES,
    python_requires=">=3.9",
    version=VERSION,
    description="IKEA Trådfri/Tradfri API. Control and observe your "
    "lights from Python.",
    long_description=LONG_DESCRIPTION,
    author="balloob, lwis, ggravlingen, janiversen",
    author_email="no@email.com",
    long_description_content_type="text/markdown",
    url=GITHUB_URL,
    package_data={"pytradfri": ["py.typed"]},
    include_package_data=True,
    license="MIT",
    keywords="ikea tradfri api iot light homeautomation",
    download_url=DOWNLOAD_URL,
    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Home Automation",
    ],
)
