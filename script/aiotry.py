import asyncio
import sys

sys.path.insert(0, '/usr/src/build/tinydtls/cython')

from aiocoap import Message, Context, GET  # noqa
from aiocoap.transports.tinydtls import PSK_STORE  # noqa


async def main():
    PSK_STORE[b'Client_identity'] = sys.argv[1].encode('utf-8')
    protocol = await Context.create_client_context()

    # msg = Message(code=GET, uri="coaps://192.168.0.24:5684/15004", observe=0)
    # res = yield from protocol.request(msg).response
    # print("RECEIVED STATUS", res.code)
    # print("RECEIVED PAYLOAD", res.payload.decode('utf-8'))

    request = Message(code=GET, uri="coaps://192.168.0.24:5684/15001/65540", observe=0)

    pr = protocol.request(request)

    # Note that it is necessary to start sending
    r = await pr.response
    print("First response: %s\n%r"%(r, r.payload))

    # async for r in pr.observation:
    #     print("Next result: %s\n%r"%(r, r.payload))

    it = (pr.observation)
    it = type(it).__aiter__(it)
    running = True
    while running:
        try:
            res = await type(it).__anext__(it)
        except StopAsyncIteration:
            running = False
        else:
            print("RECEIVED STATUS", res.code)
            print("RECEIVED PAYLOAD", res.payload.decode('utf-8'))


asyncio.get_event_loop().run_until_complete(main())
