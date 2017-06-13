"""Coap implementation."""
import json
import logging
import subprocess
from time import time
from functools import wraps

from ..command import Command
from ..error import RequestError, RequestTimeout, ClientError, ServerError

_LOGGER = logging.getLogger(__name__)

CLIENT_ERROR_PREFIX = '4.'
SERVER_ERROR_PREFIX = '5.'


def api_factory(host, security_code):
    """Generate a request method."""
    def base_command(method):

        """Return base command."""
        return [
            'coap-client',
            '-k',
            security_code,
            '-v',
            '0',
            '-m',
            method
        ]

    def _execute(api_command):
        """Execute the command."""

        if api_command.observe:
            _observe(api_command)
            return

        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        timeout = api_command.timeout
        url = api_command.url(host)

        command = base_command(method)

        kwargs = {
            'stderr': subprocess.DEVNULL,
            'timeout': timeout,
            'universal_newlines': True,
        }

        if data is not None:
            kwargs['input'] = json.dumps(data)
            command.append('-f')
            command.append('-')
            _LOGGER.debug('Executing %s %s %s: %s', host, method, path, data)
        else:
            _LOGGER.debug('Executing %s %s %s', host, method, path)

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

    def request(*api_commands):
        """Make a request."""
        if len(api_commands) == 1:
            return _execute(api_commands[0])

        command_results = []

        for api_command in api_commands:
            result = _execute(api_command)
            command_results.append(result)

        return command_results

    def _observe(api_command):
        """Observe an endpoint."""
        path = api_command.path
        duration = api_command.observe_duration
        url = api_command.url(host)
        err_callback = api_command.err_callback

        command = base_command('get') + ['-s', str(duration), url]

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

    # This will cause a RequestError to be raised if credentials invalid
    request(Command('get', ['status']))

    return request


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
