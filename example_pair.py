#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used to pair new
devices.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 example_pair.py <IP> <KEY>

Where <IP> is the address to your IKEA gateway and
<KEY> is found on the back of your IKEA gateway.
"""

import asyncio
import logging
import sys

from pytradfri import Gateway
from pytradfri.command import Command
from pytradfri.const import ROOT_DEVICES
from pytradfri.api.aiocoap_api import APIFactory


logging.basicConfig(level=logging.INFO)


@asyncio.coroutine
def run(shutdown):
    # initialization is copy/pasted from example_async.py

    # Assign configuration variables.
    # The configuration check takes care they are present.
    api_factory = APIFactory(sys.argv[1])
    with open('gateway_psk.txt', 'a+') as file:
        file.seek(0)
        psk = file.read()
        if psk:
            api_factory.psk = psk.strip()
        else:
            psk = yield from api_factory.generate_psk(sys.argv[2])
            print('Generated PSK: ', psk)
            file.write(psk)
    api = api_factory.request

    gateway = Gateway()

    # end copy/pasted

    #
    # set and regularly renew the commissioning timeout, remove when done
    #

    @asyncio.coroutine
    def keep_commissioning_alive(readiness):
        try:
            while True:
                yield from api(gateway.set_commissioning_timeout(60))
                if readiness is not None:
                    readiness()
                readiness = None
                yield from asyncio.sleep(45)
        finally:
            yield from api(gateway.set_commissioning_timeout(00))

    commissioning_ready = asyncio.Future()
    commissioning = asyncio.Task(keep_commissioning_alive(
        lambda: commissioning_ready.set_result(None)))

    #
    # monitor the device list and give instructions
    #

    last_devices = None

    def devices_updated(result):
        nonlocal last_devices

        if last_devices is None:
            print("Originally, %s device(s) are known" % len(result))
        else:
            for r in result:
                if r not in last_devices:
                    asyncio.Task(new_device(r))

        last_devices = result

    @asyncio.coroutine
    def new_device(devno):
        nonlocal commissioning

        print("New device, fetching details...", end="", flush=True)

        device_command = gateway.get_device(devno)
        device = yield from api(device_command)

        print()

        print("  New device description: %s" % (device,))

        if commissioning:
            if device.has_light_control:
                print("That was not in the expected sequence: This device was"
                      " a light and not a controller. You can still pair"
                      " another controller device.")
            else:
                print("Found a controller. You can now go ahead and add light"
                      " bulbs by pairing them to the switch as you would do"
                      " without a gateway. Press Ctrl-C when done.")
                commissioning.cancel()
                commissioning = None
                # if you wanted to implemente infinite-commissioning mode, you
                # should cancel or restart keep_commissioning_alive in a way
                # that resets the timeout, because the timeout will have gone
                # to 0 the moment the device was added.
        else:
            if not device.has_light_control:
                print("That was unexpected: A controller showed up even though"
                      " the gateway was not in pairing mode any more.")
            else:
                print("You can still add more light bulbs; press Ctrl-C when"
                      " done.")

    observe_devices = Command('get', [ROOT_DEVICES], observe=True,
                              process_result=devices_updated)
    yield from api(observe_devices)
    yield from commissioning_ready

    print("Ready to start: Gateway is in commissioning mode.")
    print("Pressing the pairing button on a switch, dimmer or motion detector"
          " for 10s near the gateway until the gateway blinks fast. A few"
          " seconds later, it the new device shows up here. You may need to"
          " switch off light bulbs in the immediate vicinity (?).")

    #
    # run until the outer loop says not to any more
    #

    yield from shutdown

    if commissioning is not None:
        print("Please allow for the commissioning mode to be disabled")
        commissioning.cancel()


if __name__ == "__main__":
    shutdown = asyncio.Future()
    main = run(shutdown)
    try:
        asyncio.get_event_loop().run_until_complete(main)
    except KeyboardInterrupt:
        shutdown.set_result(None)
        asyncio.get_event_loop().run_until_complete(main)
