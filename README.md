# Pytradfri #

This is a Python class to communicate with the [IKEA Trådfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Tradfri) ZigBee-based Gateway. Using this library you can, by communicating with the gateway, control IKEA lights (including the RGB ones) and also Philips Hue bulbs. Some of the features include:

- Get information on the gateway
- Observe lights, groups and other resources and get notified when they change
- List all devices connected to gateway
- List all lights and get attributes of lights (name, state, color temp, dimmer level etc)
- Change attribute values of lights (name, state, color temp, dimmer level etc)
- Restart and reset gateway
- List smart tasks (wake up, on/off and not home) and their attributes
- Alter values in smart tasks (some of these features not available in app yet)

Table of contents:

1. [Installation](#1-installation)
2. [Stand-alone use (command-line interface)](#2-stand-alone-use-command-line-interface)
3. [Implement in your own Python platform](#3-implement-in-your-own-python-platform)
4. [Docker support](#4-docker-support)
5. [Acknowledgements](#5-acknowledgements)

## 1. Installation
In order to use the code, you first need to install [libcoap](https://github.com/obgm/libcoap)(sync), or cython3, [tinydtls](https://git.fslab.de/jkonra2m/tinydtls) and [aiocoap](https://github.com/chrysn/aiocoap) depending on which functionality you're interested in, as per the following instructions (you might have to use sudo for some commands to work).

For synchronous functionality please install libcoap using [this script.](script/install-coap-client.sh).

For asynchronous functionality please install tinydtls and the tinydtls branch for aiocoap using [this script.](script/install-aiocoap.sh).


## 2. Stand-alone use (command-line interface)
![Screenshot of command line interface](./docs/pytradfri_cli.png)

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
api(lights[1].light_control.set_dimmer(50))
```

Observe a light for changes:

```python
def change_listener(device):
  print(device.name + " is now " + str(device.light_control.lights[0].state))

api(lights[0].observe(change_listener))
```

## 3. Implement in your own Python platform
Please see the files, example_sync.py, or example_async.py.

## 4. Docker support

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go for both sync and async. After launching, follow the above instructions to test the library stand-alone.

## 5. Acknowledgements
This is an implementation based on analysis [I](https://github.com/ggravlingen/) found [here](https://bitsex.net/software/2017/coap-endpoints-on-ikea-tradfri/) by [vidarlo](https://bitsex.net/).

A lot of work was also put in by Paulus Schoutsen ([@balloob](https://github.com/balloob)) who took the initial code concept into this library. Further work was done by Lewis Juggins ([@lwis](https://github.com/lwis)) to take the library to 2.0 with support for asyncio and 3.0 with more effective management of dependencies and consistency around return types. Lennart Buhl [@r41d](https://github.com/r41d) and Maciej Sokołowski [@matemaciek](https://github.com/matemaciek) made sure the library is supporting RGB bulbs.
