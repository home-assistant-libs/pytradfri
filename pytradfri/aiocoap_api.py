"""Coap implementation using aiocoap."""
import json
import logging

import asyncio
from aiocoap import Message, Context, GET, PUT
from aiocoap.transports.tinydtls import PSK_STORE
from pytradfri.command import Command
from .parser import process_output

_LOGGER = logging.getLogger(__name__)


def api_factory(host, security_code):
    """Generate a request method."""

    PSK_STORE[b'Client_identity'] = security_code.encode('utf-8')

    @asyncio.coroutine
    def request(api_command):
        """Make a request."""
        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        timeout = api_command.timeout
        url = api_command.url(host)
        callback = api_command.callback

        if api_command.observe:
            yield from _observe(url, callback, api_command.observe_duration)
            return

        kwargs = {}

        if data is not None:
            kwargs['payload'] = json.dumps(data).encode('utf-8')
            _LOGGER.debug('Executing %s %s %s: %s', host, method, path, data)
        else:
            _LOGGER.debug('Executing %s %s %s', host, method, path)

        api_method = GET
        if method == 'put':
            api_method = PUT

        protocol = yield from Context.create_client_context()
        msg = Message(code=api_method, uri=url, **kwargs)
        res = yield from protocol.request(msg).response
        _LOGGER.debug("RECEIVED STATUS", res.code)
        _LOGGER.debug("RECEIVED PAYLOAD", res.payload.decode('utf-8'))

        api_command.result = process_output(res, parse_json)
        return api_command.result

    @asyncio.coroutine
    def _observe(url, callback, duration):
        """Observe an endpoint."""
        protocol = yield from Context.create_client_context()

        msg = Message(code=GET,
                      uri=url,
                      observe=duration)

        pr = protocol.request(msg)

        # Note that it is necessary to start sending
        r = yield from pr.response
        _LOGGER.debug("First response: %s\n%r" % (r, r.payload))

        it = pr.observation
        it = type(it).__aiter__(it)
        running = True
        while running:
            try:
                res = yield from type(it).__anext__(it)
            except StopAsyncIteration:
                running = False
            else:
                output = res.payload.decode('utf-8')
                _LOGGER.debug("RECEIVED STATUS", res.code)
                _LOGGER.debug("RECEIVED PAYLOAD", output)
                result = process_output(output)
                callback(result)

    # This will cause a RequestError to be raised if credentials invalid
    request(Command('get', ['status']))

    return request
