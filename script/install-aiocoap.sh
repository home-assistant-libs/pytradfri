#!/bin/sh
git clone --depth 1 https://git.fslab.de/jkonra2m/tinydtls
cd tinydtls
autoreconf
./configure --with-ecc
make
cd cython
pip3 install cython
python3 setup.py build_ext --inplace

cd ../..
git clone --depth 1 -b patch-1 https://github.com/balloob/aiocoap/
cd aiocoap
python3 setup.py develop
