[![PyPI version](https://badge.fury.io/py/pytradfri.svg)](https://badge.fury.io/py/pytradfri)

Python package to communicate with the [IKEA Trådfri](http://www.ikea.com/us/en/catalog/products/00337813/) (Tradfri) ZigBee gateway compatible with ZigBee light link products. By using this library you can communicate with the gateway and control IKEA's lights, wall plugs and other peripherals.

This library is [strictly typed](https://docs.python.org/3/library/typing.html).

<b>Some of the features include:</b>

- Gateway:
  - Get information on the gateway, list all devices connected to the gateway, and restart and reset the gateway
- Any connected device or group:
  - Observe state and get notified when it changes
- Lights:

  - List all lights, get and control attributes of lights (name, state, color temp, dimmer level etc)

- Wall plugs:
  - List all wall plungs, and control wall plugs
- Air purifier
  - List all purifiers, control fan level, and get air quality level
- Window blind
  - List all blinds, control cover level, and get battery level
- Smart tasks:
  - List smart tasks (wake up, on/off and not home) and their attributes
  - Alter values in smart tasks (some of these features not available in app yet)

Table of contents:

1. [Installation](#installation)
2. [Verified Device Compatibility](#verified-device-compatibility)
3. [Stand-alone use (command-line interface)](#stand-alone-use-command-line-interface)
4. [Implement in your own Python platform](#implement-in-your-own-python-platform)
5. [Docker support](#docker-support)
6. [Known issues](#known-issues)
7. [Contributions](#contributions)

## Installation

The easiest way of getting started is by running this library in [VS Code online](https://open.vscode.dev/home-assistant-libs/pytradfri), or by installing it locally using the included containerized development environment for VS Code.

For other installation methods, you might have to use superuser privileges (sudo) for some commands to work when installing.

To use the library in a synchronous application, you first need to install [libcoap](https://github.com/obgm/libcoap) using [this script](script/install-coap-client.sh). Use [examples/example_sync.py](https://github.com/ggravlingen/pytradfri/blob/master/examples/example_sync.py) when testing this.

For asynchronous applications you will need to install `pytradfri[async]`, for instance using the requirements file: `pip install pytradfri[async]`. Please note that install might take considerable time on slow devices. Use [examples/example_async.py](https://github.com/ggravlingen/pytradfri/blob/master/examples/example_async.py) when testing this.

Security best practice is to **_not_** store the security code that is printed on the gateway permanently in your application. Please always use the PSK when communicating with the gateway.

## Verified Device Compatibility

| Device                         | Version |
| ------------------------------ | ------- |
| IKEA Gateway (E1526)           | 1.19.32 |
| TRADFRI bulb E14 WS opal 400lm | 1.2.217 |
| TRADFRI bulb E14 WS 470lm      | 2.3.087 |
| TRADFRI bulb E27 WS opal 980lm | 2.3.087 |
| TRADFRI bulb E27 W opal 1000lm | 2.3.086 |
| TRADFRI remote control         | 2.3.014 |
| TRADFRI motion sensor          | 1.2.214 |
| TRADFRI wall plug              | 2.0.022 |
| Starkvind air purifier         | 1.1.001 |

## Stand-alone use (command-line interface)

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

## Implement in your own Python platform

Please see the example files.

## Docker support

There is a Docker script available to bootstrap a dev environment. Run `./script/dev_docker` and you will build and launch a container that is ready to go for both sync and async. After launching, follow the above instructions to test the library stand-alone.

The working directory of the Docker image is `/usr/src/app`. The checked out version of this repo is added there and installed as a Python dependency for easy development and testing. When you want to use the latest stable version from pip, you only have to change to another working directory.

## Known issues

We are aware of issues some users face with their gateways. Anecdotal evicence suggests sending many requests (spamming) the gateway, or an unreliable network connection can be the culprit. As a first solution, try to limit the number of requests, and move the Gateway closer to the device running pytradfri on the nework. Other than that, there is unfortunately not anything this project can do to support or resolve these issues at this time. As this progresses, we will ensure the project is kept up-to-date.

## Contributions

We encourage contributions to this library. Please make sure contributions meet these requirements:

- Your contribution contains [type annotations](https://docs.python.org/3/library/typing.html). This is a strictly typed library: new contributions will not be merged unless they contain type annotations.
- Your contribution is covered by tests.
