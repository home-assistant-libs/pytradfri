FROM resin/rpi-raspbian:stretch

# https://community.home-assistant.io/t/ikea-tradfri-gateway-zigbee-very-basic-working-implementation/14788/19?u=balloob
RUN apt-get update -y && \
  apt-get install -y python3 python3-dev python3-pip git autoconf automake libtool make && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* build/

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./script/install-coap-client.sh install-coap-client.sh
RUN ./install-coap-client.sh

# Cython version must match the version used in DTLSSocket that's in requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install Cython==0.27.2

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

CMD /bin/bash
