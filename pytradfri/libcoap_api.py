"""Coap implementation."""
import json
import logging
import subprocess
from time import time

from pytradfri.command import Command
from .parser import process_output
from .error import RequestError, RequestTimeout

_LOGGER = logging.getLogger(__name__)


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
            _observe(path, url, callback, api_command.observe_duration)
            return

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

        api_command.result = process_output(return_value, parse_json)
        return api_command.result

    def _observe(path, url, callback, duration):
        """Observe an endpoint."""
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
                break

            if data == '{':
                open_obj += 1
            elif data == '}':
                open_obj -= 1

            output += data

            if open_obj == 0:
                result = process_output(output)
                callback(result)
                output = ''

    # This will cause a RequestError to be raised if credentials invalid
    request(Command('get', ['status']))

    return request
