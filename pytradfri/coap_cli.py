"""Coap implementation."""
import json
import logging
import subprocess

from .error import RequestError, ClientError, ServerError, RequestTimeout

_LOGGER = logging.getLogger(__name__)


CLIENT_ERROR_PREFIX = '4.'
SERVER_ERROR_PREFIX = '5.'


def api_factory(host, security_code):
    """Generate a request method."""
    def base_command(method):
        """Return base commmand."""
        return [
            'coap-client',
            '-k',
            security_code,
            '-v',
            '0',
            '-m',
            method
        ]

    def url(path):
        """Generate url for coap client."""
        path = '/'.join(str(v) for v in path)
        return 'coaps://{}:5684/{}'.format(host, path)

    def request(method, path, data=None, *, parse_json=True, timeout=10):
        """Make a request."""
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

        command.append(url(path))

        try:
            return_value = subprocess.check_output(command, **kwargs)
        except subprocess.TimeoutExpired:
            raise RequestTimeout() from None
        except subprocess.CalledProcessError as err:
            raise RequestError(
                'Error executing request: %s'.format(err)) from None

        return _process_output(return_value.strip(), parse_json)

    def observe(path, callback, time):
        """Observe an endpoint."""
        command = base_command('get') + ['-s', str(time), url(path)]
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
        in_string = False
        for data in iter(lambda: proc.stdout.read(1), ''):
            output += data

            if data == '"':
                in_string = not in_string
            elif in_string:
                pass
            elif data == '{':
                open_obj += 1
            elif data == '}':
                open_obj -= 1

            if open_obj == 0:
                callback(_process_output(output))
                output = ''

    request.observe = observe

    # This will cause a RequestError to be raised if credentials invalid
    request('get', ['status'])

    return request


def _process_output(output, parse_json=True):
    """Process output."""
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
