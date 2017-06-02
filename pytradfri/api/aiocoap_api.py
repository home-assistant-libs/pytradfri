"""Coap implementation using aiocoap."""
import asyncio
import json
import logging
import sys

sys.path.insert(0, '/usr/src/build/tinydtls/cython')

import aiocoap
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code
from aiocoap.transports.tinydtls import TransportEndpointTinyDTLS
from async_timeout import timeout

from pytradfri.error import ClientError, ServerError
from pytradfri.command import Command

_LOGGER = logging.getLogger(__name__)


class PatchedDTLSSecurityStore:
    """Patched DTLS store in lieu of impl."""

    SECRET_PSK = None

    def _get_psk(self, host, port):
        return b"Client_identity", PatchedDTLSSecurityStore.SECRET_PSK


aiocoap.transports.tinydtls.DTLSSecurityStore = PatchedDTLSSecurityStore


def _patched_datagram_received(self, data, addr):
    self._dtls_socket.handleMessage(self._connection, data, 0)

aiocoap.transports.tinydtls.DTLSClientConnection.datagram_received = _patched_datagram_received


@asyncio.coroutine
def api_factory(host, security_code):
    """Generate a request method."""

    security_code = security_code.encode('utf-8')

    PatchedDTLSSecurityStore.SECRET_PSK = security_code

    @asyncio.coroutine
    def _get_protocol():
        # TODO: Should/can this be reused?
        protocol = yield from Context.create_client_context()
        for endpoint in protocol.transport_endpoints:
            if type(endpoint) == TransportEndpointTinyDTLS:
                pass
        return protocol

    @asyncio.coroutine
    def request(api_command):
        """Make a request."""
        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        request_timeout = api_command.timeout
        url = api_command.url(host)
        callback = api_command.callback

        protocol = yield from _get_protocol()

        if api_command.observe:
            yield from _observe(protocol, url, callback,
                                api_command.observe_duration)
            return

        kwargs = {}

        if data is not None:
            kwargs['payload'] = json.dumps(data).encode('utf-8')
            _LOGGER.debug('Executing %s %s %s: %s', host, method, path, data)
        else:
            _LOGGER.debug('Executing %s %s %s', host, method, path)

        api_method = Code.GET
        if method == 'put':
            api_method = Code.PUT

        msg = Message(code=api_method, uri=url, **kwargs)
        with timeout(request_timeout):
            res = yield from protocol.request(msg).response
            api_command.result = _process_output(res, parse_json)

        return api_command.result

    @asyncio.coroutine
    def _observe(protocol, url, callback, duration):
        """Observe an endpoint."""
        msg = Message(code=Code.GET, uri=url, observe=duration)

        pr = protocol.request(msg)

        # Note that this is necessary to start observing
        r = yield from pr.response

        result = _process_output(r)
        callback(result)

        it = pr.observation
        it = type(it).__aiter__(it)
        running = True
        while running:
            try:
                res = yield from type(it).__anext__(it)
            except StopAsyncIteration:  # TODO: This was added in 3.5 :(
                running = False
            else:
                result = _process_output(res)
                callback(result)

    # This will cause a RequestError to be raised if credentials invalid
    yield from request(Command('get', ['status']))

    return request


def _process_output(res, parse_json=True):
    """Process output."""
    res_payload = res.payload.decode('utf-8')
    output = res_payload.strip()

    _LOGGER.debug('Status: %s, Received: %s', res.code, output)

    if not output:
        return None

    if not res.code.is_successful:
        if res.code >= 128 and res.code < 160:
            raise ClientError(output)
        elif res.code >= 160 and res.code < 192:
            raise ServerError(output)

    if not parse_json:
        return output

    return json.loads(output)
