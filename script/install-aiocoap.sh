#!/bin/sh
git clone --depth 1 https://git.fslab.de/jkonra2m/tinydtls.git
cd tinydtls
autoreconf
./configure --with-ecc --without-debug
cd cython
python3 setup.py install

cd ../..
git clone --depth 1 https://github.com/chrysn/aiocoap/
cd aiocoap
python3 -m pip install .
