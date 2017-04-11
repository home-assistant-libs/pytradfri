"""Coap implementation."""
import json
import logging
import subprocess

from .error import CommandError, NotFoundError

_LOGGER = logging.getLogger(__name__)


NOT_FOUND = '4.04 Not Found'


def api_factory(host, security_code):
    """Generate a request method."""
    def request(method, path, data=None, *, parse_json=True):
        """Make a request."""
        path = '/'.join(str(v) for v in path)
        command_string = 'coaps://{}:5684/{}'.format(host, path)

        command = [
            '/usr/local/bin/coap-client',
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
            'timeout': 10,
            'stderr': subprocess.STDOUT,
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
            out = return_value.strip().decode('utf-8')
        except subprocess.CalledProcessError:
            raise CommandError() from None

        # Return only the last line, where there's JSON
        lines = [line for line in out.split('\n')[1:]
                 if 'decrypt_verify' not in line]

        if not lines:
            return None

        output = lines[0]
        _LOGGER.debug('Received: %s', output)

        if not parse_json:
            return output

        if output == NOT_FOUND:
            raise NotFoundError()

        return json.loads(output)

    return request
