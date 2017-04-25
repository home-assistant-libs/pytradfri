# Pytradfri #

This is a Python class to communicate with the [IKEA Trådfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Tradfri) ZigBee-based Gateway. The gateway can control IKEA lights and also Philips Hue bulbs. Some of the features include:

- Get information on the gateway
- List all devices connected to gateway
- List all lights and get attributes of lights (name, state, color temp, dimmer level etc)
- Change attribute values of lights (name, state, color temp, dimmer level etc)
- List smart tasks (wake up, on/off and not home) and their attributes
- Observe lights, groups and other resources and get notified when they change

Table of contents:

1. [Installation](#1-installation)
2. [Stand-alone use (command-line interface)](#2-stand-alone-use-command-line-interface)
3. [Implement in your own Python platform](#3-implement-in-your-own-python-platform)
4. [Docker support](#4-docker-support)
5. [Acknowledgements](#5-acknowledgements)

## 1. Installation
In order to use the code, you first need to install [libcoap](https://github.com/obgm/libcoap) as per the following instructions (you might have to use sudo for some commands to work):

```shell
$ apt-get install libtool

$ git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
$ cd libcoap
$ ./autogen.sh
$ ./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
$ make
$ make install
```

## 2. Stand-alone use (command-line interface)
If you want to test this library stand-alone in a command-line interface:

```shell
$ python3 -i -m pytradfri IP KEY
```
Where the following variables are substituted:
- **IP** is the IP-address to your gateway.
- **KEY** is written on the back of your IKEA Tradfri Gateway.

### Examples of commands in the stand-alone prompt:

List all lights:

```python
lights
```

Set brightnes of item 1 to 50 in lights list:

```python
lights[1].light_control.set_dimmer(50)
```

Observe a light for changes:

```python
def change_listener(device):
  print(device.name + " is now " + str(device.light_control.lights[0].state))

lights[0].observe(change_listener)
```

## 3. Implement in your own Python platform
```
#!/usr/bin/env python3

# put all of this in test_pytradfri.py
# Run by executing the following command from shell, from the same folder you have stored test_pytradfri.py in.
# python3 test_pytradfri.py IP KEY

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

# Example 6: Return the transition time (in minutes) for task#1
tasks[0].task_control.tasks[0].transition_time
```

## 4. Docker support

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go. After launching, follow the above instructions to test the library stand-alone.

## 5. Acknowledgements
This is an implementation based on analysis [I](https://github.com/ggravlingen/) found [here](https://bitsex.net/software/2017/coap-endpoints-on-ikea-tradfri/) by [vidarlo](https://bitsex.net/).

A lot of work was also put in by Paulus Schoutsen ([@balloob](https://github.com/balloob)) who took the initial code concept into this library.
