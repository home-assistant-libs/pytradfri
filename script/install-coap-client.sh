#!/bin/sh

if [ "$EUID" -ne 0 ]
  then echo "Please run the script as: sudo ./install-coap-client.sh"
  exit
fi

apt-get install -f autoconf automake libtool  

git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
cd libcoap
./autogen.sh
./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
make
make install
