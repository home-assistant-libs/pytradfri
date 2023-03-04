#!/usr/bin/env python3
"""Example pairing.

This is an example of how the pytradfri-library can be used to pair new
devices.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_pair.py)
$ python3 example_pair.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""
from __future__ import annotations

import argparse
import asyncio
from collections.abc import Callable
import logging
import os
import sys
import uuid

# Hack to allow relative import above top level package

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# pylint: disable=import-error, wrong-import-position

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.command import Command
from pytradfri.const import ROOT_DEVICES
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "tradfri_standalone_psk.conf"

# pylint: disable=invalid-name


parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
)
parser.add_argument(
    "-K", "--key", dest="key", required=False, help="Key found on your Tradfri gateway"
)
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
        "Please provide the 'Security Code' on the back of your Tradfri gateway:",
        end=" ",
    )
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")

    args.key = key


async def run(shutdown: asyncio.Future[None]) -> None:
    """Run."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get("identity")
        psk = conf[args.host].get("key")
        api_factory = await APIFactory.init(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = await APIFactory.init(host=args.host, psk_id=identity)

        try:
            psk = await api_factory.generate_psk(args.key)
            print("Generated PSK: ", psk)

            conf[args.host] = {"identity": identity, "key": psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError as err:
            raise PytradfriError(
                "Please provide the 'Security Code' on the "
                "back of your Tradfri gateway using the "
                "-K flag."
            ) from err

    api = api_factory.request

    gateway = Gateway()

    # end copy/pasted

    #
    # set and regularly renew the commissioning timeout, remove when done
    #

    async def keep_commissioning_alive(readiness: Callable[[], None]) -> None:
        readiness_called = False
        try:
            while True:
                await api(gateway.set_commissioning_timeout(60))
                if not readiness_called:
                    readiness()
                    readiness_called = True
                await asyncio.sleep(45)
        finally:
            await api(gateway.set_commissioning_timeout(0))

    commissioning_ready: asyncio.Future[None] = asyncio.Future()
    commissioning: asyncio.Task[None] | None
    commissioning = asyncio.create_task(
        keep_commissioning_alive(lambda: commissioning_ready.set_result(None))
    )

    #
    # monitor the device list and give instructions
    #

    last_devices: list[str] | None = None

    def devices_updated(result: list[str]) -> None:
        nonlocal last_devices

        if last_devices is None:
            print(f"Originally, {len(result)} device(s) are known")
        else:
            for r in result:
                if r not in last_devices:
                    asyncio.create_task(new_device(r))

        last_devices = result

    async def new_device(device_id: str) -> None:
        nonlocal commissioning

        print("New device, fetching details...", end="", flush=True)

        device_command = gateway.get_device(device_id)
        device = await api(device_command)

        print()

        print(f"  New device description: {(device,)}")

        if commissioning:
            if device.has_light_control:
                print(
                    "That was not in the expected sequence: This device was"
                    " a light and not a controller. You can still pair"
                    " another controller device."
                )
            else:
                print(
                    "Found a controller. You can now go ahead and add light"
                    " bulbs by pairing them to the switch as you would do"
                    " without a gateway. Press Ctrl-C when done."
                )
                commissioning.cancel()
                commissioning = None
                # if you wanted to implement infinite-commissioning mode, you
                # should cancel or restart keep_commissioning_alive in a way
                # that resets the timeout, because the timeout will have gone
                # to 0 the moment the device was added.
        else:
            if not device.has_light_control:
                print(
                    "That was unexpected: A controller showed up even though"
                    " the gateway was not in pairing mode any more."
                )
            else:
                print("You can still add more light bulbs; press Ctrl-C when done.")

    observe_devices = Command(
        "get", [ROOT_DEVICES], observe=True, process_result=devices_updated
    )
    await api(observe_devices)
    await commissioning_ready

    print("Ready to start: Gateway is in commissioning mode.")
    print(
        "Pressing the pairing button on a switch, dimmer or motion detector"
        " for 10s near the gateway until the gateway blinks fast. A few"
        " seconds later, it the new device shows up here. You may need to"
        " switch off light bulbs in the immediate vicinity (?)."
    )

    #
    # run until the outer loop says not to any more
    #

    await api_factory.shutdown()
    await shutdown

    if commissioning is not None:
        print("Please allow for the commissioning mode to be disabled")
        commissioning.cancel()
        commissioning = None


if __name__ == "__main__":
    shutdown_future: asyncio.Future[None] = asyncio.Future()
    main = run(shutdown_future)
    try:
        asyncio.run(main)
    except KeyboardInterrupt:
        shutdown_future.set_result(None)
        asyncio.run(main)
