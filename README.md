[![Coverage Status](https://coveralls.io/repos/github/ggravlingen/pytradfri/badge.svg?branch=master)](https://coveralls.io/github/ggravlingen/pytradfri?branch=master)
[![PyPI version](https://badge.fury.io/py/pytradfri.svg)](https://badge.fury.io/py/pytradfri)

**NB:** Latest Gateway version tested and working - 1.4.15.

Python class to communicate with the [IKEA Trådfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Tradfri) ZigBee-based Gateway. By using this library you can communicate with the gateway and control IKEA's lights and wall plugs.
 Some of the features include:

- Get information on the gateway
- Observe lights, groups and other resources and get notified when they change
- Control wall plugs
- List all devices connected to gateway
- List all lights and get attributes of lights (name, state, color temp, dimmer level etc)
- Change attribute values of lights (name, state, color temp, dimmer level etc)
- Restart and reset the gateway
- List smart tasks (wake up, on/off and not home) and their attributes
- Alter values in smart tasks (some of these features not available in app yet)

Table of contents:

1. [Installation](#1-installation)
2. [Stand-alone use (command-line interface)](#2-stand-alone-use-command-line-interface)
3. [Implement in your own Python platform](#3-implement-in-your-own-python-platform)
4. [Docker support](#4-docker-support)
5. [Acknowledgements](#5-acknowledgements)

## 1. Installation
You might have to use superuser privileges (sudo) for some commands to work when installing.

To use the library in a synchronous application, you first need to install [libcoap](https://github.com/obgm/libcoap) using [this script](script/install-coap-client.sh). Use [examples/example_sync.py](https://github.com/ggravlingen/pytradfri/blob/master/examples/example_sync.py) when testing this.

For asynchronous applications you will need to install [DTLSSocket](https://pypi.python.org/pypi/DTLSSocket), for instance using the requirements file: ```shell pip install -r requirements.txt ```. Please note that install might take considerable time on slow devices. Use [examples/example_async.py](https://github.com/ggravlingen/pytradfri/blob/master/examples/example_async.py) when testing this.

Security best practice is to ***not*** store the security code that is printed on the gateway permanently in your application. Please always use the PSK when communicating with the gateway.

## 2. Stand-alone use (command-line interface)
![Screenshot of command line interface](./docs/pytradfri_cli.png)

If you want to test this library stand-alone in a command-line interface:

```shell
$ python3 -i -m pytradfri IP
```
Where **IP** is substituted by the IP-address to your gateway.

The first time running pytradfri you will be asked to input the 'Security Code' found on the back of your IKEA gateway.

### Examples of commands in the stand-alone prompt:

List all lights:

```python
lights
```

Set the brightness of item 1 to 50 in lights list:

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
Please see the example files.

## 4. Docker support

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go for both sync and async. After launching, follow the above instructions to test the library stand-alone.

## 5. Acknowledgements
This is an implementation based on analysis [I](https://github.com/ggravlingen/) found [here](https://bitsex.net/software/2017/coap-endpoints-on-ikea-tradfri/) by [vidarlo](https://bitsex.net/).

Paulus Schoutsen ([@balloob](https://github.com/balloob)) made a working Python library of the initial code concept. Lewis Juggins ([@lwis](https://github.com/lwis)) added support for asyncio and improved management of dependencies and consistency around return types. Many others have [contributed](https://github.com/ggravlingen/pytradfri/graphs/contributors) too.
