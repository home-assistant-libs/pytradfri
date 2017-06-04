"""Coap implementation using aiocoap."""
import asyncio
import json
import logging
import sys

sys.path.insert(0, '/usr/src/build/tinydtls/cython')  # noqa

import aiocoap
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code
from aiocoap.transports.tinydtls import TransportEndpointTinyDTLS
from async_timeout import timeout

from ..error import ClientError, ServerError
from ..command import Command

_LOGGER = logging.getLogger(__name__)


class PatchedDTLSSecurityStore:
    """Patched DTLS store in lieu of impl."""

    SECRET_PSK = None

    def _get_psk(self, host, port):
        return b"Client_identity", PatchedDTLSSecurityStore.SECRET_PSK


aiocoap.transports.tinydtls.DTLSSecurityStore = PatchedDTLSSecurityStore


def _patched_datagram_received(self, data, addr):
    self._dtls_socket.handleMessage(self._connection, data, 0)


aiocoap.transports.tinydtls.DTLSClientConnection.datagram_received = \
    _patched_datagram_received


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
        protocol = yield from _get_protocol()

        if api_command.observe:
            yield from _observe(protocol, api_command)
            return

        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        request_timeout = api_command.timeout
        url = api_command.url(host)

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
    def _observe(protocol, api_command):
        """Observe an endpoint."""
        duration = api_command.observe_duration
        url = api_command.url(host)
        err_callback = api_command.err_callback

        msg = Message(code=Code.GET, uri=url, observe=duration)

        pr = protocol.request(msg)

        # Note that this is necessary to start observing
        r = yield from pr.response
        api_command.result = _process_output(r)

        def success_callback(res):
            api_command.result = _process_output(res)

        def error_callback(ex):
            err_callback(ex)

        ob = pr.observation
        ob.register_callback(success_callback)
        ob.register_errback(error_callback)

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
