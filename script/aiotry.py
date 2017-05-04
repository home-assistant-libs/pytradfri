import asyncio
import sys

sys.path.insert(0, '/usr/src/build/tinydtls/cython')

from aiocoap import Message, Context, GET  # noqa
from aiocoap.transports.tinydtls import PSK_STORE  # noqa


@asyncio.coroutine
def main():
    if len(sys.argv) < 2:
        print("Pass in key as second argument")
        return

    PSK_STORE[b'Client_identity'] = sys.argv[1].encode('utf-8')

    msg = Message(code=GET, uri="coaps://192.168.1.19:5684/15001")
    protocol = yield from Context.create_client_context()
    res = yield from protocol.request(msg).response
    print("RECEIVED STATUS", res.code)
    print("RECEIVED PAYLOAD", res.payload.decode('utf-8'))


asyncio.get_event_loop().run_until_complete(main())
