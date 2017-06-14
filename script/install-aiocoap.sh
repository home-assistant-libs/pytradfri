#!/bin/sh
git clone --depth 1 https://git.fslab.de/jkonra2m/tinydtls
cd tinydtls
autoreconf
./configure --with-ecc --without-debug
cd cython
python3 setup.py install

cd ../..
git clone --depth 1 -b tinydtls https://github.com/chrysn/aiocoap/
cd aiocoap
python3 -m pip install .
