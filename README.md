# Pytradfri

This is a Python class to communicate with the [IKEA Tradfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Trådfri) ZigBee-based Gateway. The gateway can control IKEA lights and also Philips Hue bulbs.

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

### Examples of commands in the stand-alone prompt:

List all lights: 
```shell
lights
```
Set brightnes of item 1 to 50 in lights list: 
```shell
lights[1].set_light_brightness(50)
```


## Implement in your own Python platform
```
#!/usr/bin/env python3

# put all of this in test_pytradfri.py
# Run by executing the following command from shell, from the same folder you have stored test_pytradfri.py in.
# python3 -m test_pytradfri IP KEY

# Pre-requisites
# pip3 install pytradfri

import sys
import pytradfri

# Assign configuration variables. The configuration check takes care they are present.
api = pytradfri.coap_cli.api_factory(sys.argv[1], sys.argv[2])
gateway = pytradfri.gateway.Gateway(api)
devices = gateway.get_devices()
lights = [dev for dev in devices if dev.has_light_control]

# Print all lights
print(lights)

# Lights can be accessed by its index, so lights[1] is the second light

# Example 1: checks state of the light 2 (true=on)
print(lights[1].light_control.lights[0].state)

# Example 2: get dimmer level of light 2
print(lights[1].light_control.lights[0].dimmer)

# Example 3: What is the name of light 2
print(lights[1].name)

# Example 4: Set the light level of light 2
lights[1].light_control.set_dimmer(20)

# Example 5: Change color of light 2
lights[1].light_control.set_hex_color('f5faf6') # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
```

### Docker

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go. After launching, follow the above instructions to test the library stand-alone.
