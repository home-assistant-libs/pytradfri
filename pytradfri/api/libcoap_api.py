"""Coap implementation."""
import json
import logging
import subprocess
from time import time
from functools import wraps

from ..gateway import Gateway
from ..error import RequestError, RequestTimeout, ClientError, ServerError

_LOGGER = logging.getLogger(__name__)

CLIENT_ERROR_PREFIX = '4.'
SERVER_ERROR_PREFIX = '5.'


class APIFactory:
    def __init__(self, host, psk_id='pytradfri', psk=None, timeout=10):
        self._host = host
        self._psk_id = psk_id
        self._psk = psk
        self._timeout = timeout  # seconds

    @property
    def psk(self):
        return self._psk

    @psk.setter
    def psk(self, value):
        self._psk = value

    def _base_command(self, method):
        """Return base command."""
        return [
            'coap-client',
            '-u',
            self._psk_id,
            '-k',
            self._psk,
            '-v',
            '0',
            '-m',
            method
        ]

    def _execute(self, api_command, *, timeout=None):
        """Execute the command."""

        if api_command.observe:
            self._observe(api_command)
            return

        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        url = api_command.url(self._host)

        proc_timeout = self._timeout
        if timeout is not None:
            proc_timeout = timeout

        command = self._base_command(method)

        kwargs = {
            'stderr': subprocess.DEVNULL,
            'timeout': proc_timeout,
            'universal_newlines': True,
        }

        if data is not None:
            kwargs['input'] = json.dumps(data)
            command.append('-f')
            command.append('-')
            _LOGGER.debug('Executing %s %s %s: %s', self._host, method, path,
                          data)
        else:
            _LOGGER.debug('Executing %s %s %s', self._host, method, path)

        command.append(url)

        try:
            return_value = subprocess.check_output(command, **kwargs)
        except subprocess.TimeoutExpired:
            raise RequestTimeout() from None
        except subprocess.CalledProcessError as err:
            raise RequestError(
                'Error executing request: {}'.format(err)) from None

        api_command.result = _process_output(return_value, parse_json)
        return api_command.result

    def request(self, api_commands, *, timeout=None):
        """Make a request. Timeout is in seconds."""
        if not isinstance(api_commands, list):
            return self._execute(api_commands, timeout=timeout)

        command_results = []

        for api_command in api_commands:
            result = self._execute(api_command, timeout=timeout)
            command_results.append(result)

        return command_results

    def _observe(self, api_command):
        """Observe an endpoint."""
        path = api_command.path
        duration = api_command.observe_duration
        if duration <= 0:
            raise ValueError("Observation duration has to be greater than 0.")
        url = api_command.url(self._host)
        err_callback = api_command.err_callback

        command = (self._base_command('get')
                   + ['-s', str(duration), '-B', str(duration), url])

        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.DEVNULL,
            'universal_newlines': True
        }
        try:
            proc = subprocess.Popen(command, **kwargs)
        except subprocess.CalledProcessError as err:
            raise RequestError(
                'Error executing request: %s'.format(err)) from None

        output = ''
        open_obj = 0
        start = time()

        for data in iter(lambda: proc.stdout.read(1), ''):
            if data == '\n':
                _LOGGER.debug('Observing stopped for %s after %.1fs',
                              path, time() - start)
                err_callback(RequestError("Observing stopped."))
                break

            if data == '{':
                open_obj += 1
            elif data == '}':
                open_obj -= 1

            output += data

            if open_obj == 0:
                api_command.result = _process_output(output)
                output = ''

    def generate_psk(self, security_key):
        """
        Generate and set a psk from the security key.
        """
        if not self._psk:
            # Backup the real identity.
            existing_psk_id = self._psk_id

            # Set the default identity and security key for generation.
            self._psk_id = 'Client_identity'
            self._psk = security_key

            # Ask the Gateway to generate the psk for the identity.
            self._psk = self.request(Gateway().generate_psk(existing_psk_id))

            # Restore the real identity.
            self._psk_id = existing_psk_id

        return self._psk


def _process_output(output, parse_json=True):
    """Process output."""
    output = output.strip()
    _LOGGER.debug('Received: %s', output)

    if not output:
        return None

    elif 'decrypt_verify' in output:
        raise RequestError(
            'Please compile coap-client without debug output. See '
            'instructions at '
            'https://github.com/ggravlingen/pytradfri#installation')

    elif output.startswith(CLIENT_ERROR_PREFIX):
        raise ClientError(output)

    elif output.startswith(SERVER_ERROR_PREFIX):
        raise ServerError(output)

    elif not parse_json:
        return output

    return json.loads(output)


def retry_timeout(api, retries=3):
    """Retry API call when a timeout occurs."""
    @wraps(api)
    def retry_api(*args, **kwargs):
        """Retrying API."""
        for i in range(1, retries + 1):
            try:
                return api(*args, **kwargs)
            except RequestTimeout:
                if i == retries:
                    raise

    return retry_api
