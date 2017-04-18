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
    def request(method, path, data=None, *, parse_json=True, timeout=10):
        """Make a request."""

        path = '/'.join(str(v) for v in path)
        command_string = 'coaps://{}:5684/{}'.format(host, path)

        command = [
            'coap-client',
            '-u',
            'Client_identity',
            '-k',
            security_code,
            '-v',
            '0',
            '-m',
            method,
            command_string
        ]

        kwargs = {
            'timeout': timeout,
            'stderr': subprocess.DEVNULL,
        }

        if data is not None:
            kwargs['input'] = json.dumps(data).encode('utf-8')
            command.append('-f')
            command.append('-')
            _LOGGER.debug('Executing %s %s %s: %s', host, method, path, data)
        else:
            _LOGGER.debug('Executing %s %s %s', host, method, path)

        try:
            return_value = subprocess.check_output(command, **kwargs)
            output = return_value.strip().decode('utf-8')
        except subprocess.TimeoutExpired:
            raise RequestTimeout() from None
        except subprocess.CalledProcessError as err:
            raise RequestError(
                'Error executing request: %s'.format(err)) from None

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

    # This will cause a RequestError to be raised if credentials invalid
    request('get', ['status'])

    return request
