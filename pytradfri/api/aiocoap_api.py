"""COAP implementation using aiocoap."""
import asyncio
import json
import logging
import socket

from aiocoap import Message, Context
from aiocoap.error import RequestTimedOut, Error, ConstructionRenderableError
from aiocoap.numbers.codes import Code
from aiocoap.transports import tinydtls

from ..error import ClientError, ServerError, RequestTimeout
from ..gateway import Gateway

_LOGGER = logging.getLogger(__name__)


class PatchedDTLSSecurityStore:
    """Patched DTLS store in lieu of a credentials framework.
       https://github.com/chrysn/aiocoap/issues/97"""

    IDENTITY = None
    KEY = None

    def _get_psk(self, host, port):
        return PatchedDTLSSecurityStore.IDENTITY, PatchedDTLSSecurityStore.KEY


tinydtls.DTLSSecurityStore = PatchedDTLSSecurityStore


class APIFactory:
    def __init__(self, host, psk_id='pytradfri', psk=None, loop=None):
        self._psk = psk
        self._host = host
        self._psk_id = psk_id
        self._loop = loop
        self._observations_err_callbacks = []
        self._protocol = None

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        PatchedDTLSSecurityStore.IDENTITY = self._psk_id.encode('utf-8')

        if self._psk:
            PatchedDTLSSecurityStore.KEY = self._psk.encode('utf-8')

    @property
    def psk_id(self):
        return self._psk_id

    @psk_id.setter
    def psk_id(self, value):
        self._psk_id = value
        PatchedDTLSSecurityStore.IDENTITY = self._psk_id.encode('utf-8')

    @property
    def psk(self):
        return self._psk

    @psk.setter
    def psk(self, value):
        self._psk = value
        PatchedDTLSSecurityStore.KEY = self._psk.encode('utf-8')

    async def _get_protocol(self):
        """Get the protocol for the request."""
        if self._protocol is None:
            self._protocol = asyncio.Task(Context.create_client_context(
                loop=self._loop))
        return (await self._protocol)

    async def _reset_protocol(self, exc=None):
        """Reset the protocol if an error occurs."""
        # Be responsible and clean up.
        protocol = await self._get_protocol()
        await protocol.shutdown()
        self._protocol = None
        # Let any observers know the protocol has been shutdown.
        for ob_error in self._observations_err_callbacks:
            ob_error(exc)
        self._observations_err_callbacks.clear()

    async def shutdown(self, exc=None):
        """Shutdown the API events.
           This should be called before closing the event loop."""
        await self._reset_protocol(exc)

    async def _get_response(self, msg):
        """Perform the request, get the response."""
        try:
            protocol = await self._get_protocol()
            pr = protocol.request(msg)
            r = await pr.response
            return pr, r
        except ConstructionRenderableError as e:
            raise ClientError("There was an error with the request.", e)
        except RequestTimedOut as e:
            await self._reset_protocol(e)
            raise RequestTimeout('Request timed out.', e)
        except (OSError, socket.gaierror, Error) as e:
            # aiocoap sometimes raises an OSError/socket.gaierror too.
            # aiocoap issue #124
            await self._reset_protocol(e)
            raise ServerError("There was an error with the request.", e)
        except asyncio.CancelledError as e:
            await self._reset_protocol(e)
            raise e

    async def _execute(self, api_command):
        """Execute the command."""
        if api_command.observe:
            await self._observe(api_command)
            return

        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        url = api_command.url(self._host)

        kwargs = {}

        if data is not None:
            kwargs['payload'] = json.dumps(data).encode('utf-8')
            _LOGGER.debug('Executing %s %s %s: %s', self._host, method, path,
                          data)
        else:
            _LOGGER.debug('Executing %s %s %s', self._host, method, path)

        api_method = Code.GET
        if method == 'put':
            api_method = Code.PUT
        elif method == 'post':
            api_method = Code.POST
        elif method == 'delete':
            api_method = Code.DELETE
        elif method == 'fetch':
            api_method = Code.FETCH
        elif method == 'patch':
            api_method = Code.PATCH

        msg = Message(code=api_method, uri=url, **kwargs)

        _, res = await self._get_response(msg)

        api_command.result = _process_output(res, parse_json)

        return api_command.result

    async def request(self, api_commands):
        """Make a request."""
        if not isinstance(api_commands, list):
            result = await self._execute(api_commands)
            return result

        commands = (self._execute(api_command) for api_command in api_commands)
        command_results = await asyncio.gather(*commands, loop=self._loop)

        return command_results

    async def _observe(self, api_command):
        """Observe an endpoint."""
        duration = api_command.observe_duration
        url = api_command.url(self._host)
        err_callback = api_command.err_callback

        msg = Message(code=Code.GET, uri=url, observe=duration)

        # Note that this is necessary to start observing
        pr, r = await self._get_response(msg)

        api_command.result = _process_output(r)

        def success_callback(res):
            api_command.result = _process_output(res)

        def error_callback(ex):
            err_callback(ex)

        ob = pr.observation
        ob.register_callback(success_callback)
        ob.register_errback(error_callback)
        self._observations_err_callbacks.append(ob.error)

    async def generate_psk(self, security_key):
        """Generate and set a psk from the security key."""
        if not self._psk:
            PatchedDTLSSecurityStore.IDENTITY = 'Client_identity'.encode(
                'utf-8')
            PatchedDTLSSecurityStore.KEY = security_key.encode('utf-8')

            command = Gateway().generate_psk(self._psk_id)
            self._psk = await self.request(command)

            PatchedDTLSSecurityStore.IDENTITY = self._psk_id.encode('utf-8')
            PatchedDTLSSecurityStore.KEY = self._psk.encode('utf-8')

            # aiocoap has now cached our psk, so it must be reset.
            # We also no longer need the protocol, so this will clean that up.
            await self._reset_protocol()

        return self._psk


def _process_output(res, parse_json=True):
    """Process output."""
    res_payload = res.payload.decode('utf-8')
    output = res_payload.strip()

    _LOGGER.debug('Status: %s, Received: %s', res.code, output)

    if not output:
        return None

    if not res.code.is_successful():
        if 128 <= res.code < 160:
            raise ClientError(output)
        elif 160 <= res.code < 192:
            raise ServerError(output)

    if not parse_json:
        return output

    return json.loads(output)
