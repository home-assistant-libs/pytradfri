FROM python:3.11-bullseye

COPY . /usr/src/app/

RUN mkdir -p /usr/src/build && \
    cd /usr/src/build && \
    pip3 install --upgrade pip setuptools wheel cython && \
    pip3 install -r /usr/src/app/requirements.txt && \
    chmod +x /usr/src/app/script/install-coap-client.sh && \
    /usr/src/app/script/install-coap-client.sh && \
    pip3 install -e /usr/src/app/

WORKDIR /usr/src/app
