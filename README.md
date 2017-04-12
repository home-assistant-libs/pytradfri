# Pytradfri

This is a Python class to communicate with the [IKEA Tradfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Trådfri) ZigBee-based Gateway.

This is an implementation based on analysis [I](https://github.com/ggravlingen/) found [here](https://bitsex.net/software/2017/coap-endpoints-on-ikea-tradfri/) by [vidarlo](https://bitsex.net/).

A lot of work was also put in by Paulus Schoutsen ([@balloob](https://github.com/balloob)) who took the initial code concept into this library.


## Installation
In order to use the code, you first need to install [libcoap](https://github.com/obgm/libcoap) as per the following instructions:

```shell
$ apt-get install libtool

$ git clone --recursive https://github.com/obgm/libcoap.git
$ cd libcoap
$ git checkout dtls
$ git submodule update --init --recursive
$ ./autogen.sh
$ ./configure --disable-documentation --disable-shared
$ make
$ sudo make install
```
## Stand-alone
If you want to test this library stand-alone:

```shell
$ python3 -i -m pytradfri IP KEY
```
Where the following variables are substituted:
- **IP** is the IP-address to your gateway.
- **KEY** is written on the back of your IKEA Tradfri Gateway.

### Examples of commands in the prompt:

List all lights: 
```shell
lights
```
Set brightnes of item 1 to 50 in lights list: 
```shell
lights[1].set_light_brightness(50)
```

### Docker

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go. After launching, follow the above instructions to test the library stand-alone.
