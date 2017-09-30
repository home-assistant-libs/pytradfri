#!/bin/sh
git clone --depth 1 https://git.fslab.de/jkonra2m/tinydtls.git
cd tinydtls
autoreconf
./configure --with-ecc --without-debug
cd cython
python3 setup.py install

cd ../..
git clone --depth 1 https://github.com/chrysn/aiocoap
cd aiocoap
git reset --hard 0df6a1e44582de99ae944b6a7536d08e2a612e8f
python3 -m pip install --upgrade pip setuptools
python3 -m pip install .
