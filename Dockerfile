FROM debian:latest

# https://community.home-assistant.io/t/ikea-tradfri-gateway-zigbee-very-basic-working-implementation/14788/19?u=balloob
RUN apt-get update -y && \
  apt-get install -y python3 python3-pip git autoconf automake libtool && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* build/

RUN mkdir -p /usr/src/app /usr/src/build
WORKDIR /usr/src/build

RUN python3 -m pip install cython

COPY ./script/install-coap-client.sh install-coap-client.sh
RUN ./install-coap-client.sh

COPY ./script/install-aiocoap.sh install-aiocoap.sh
RUN ./install-aiocoap.sh

WORKDIR /usr/src/app
CMD /bin/bash
