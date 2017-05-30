import json
import logging

from .error import RequestError, ClientError, ServerError, RequestTimeout

_LOGGER = logging.getLogger(__name__)

CLIENT_ERROR_PREFIX = '4.'
SERVER_ERROR_PREFIX = '5.'


def process_output(output, parse_json=True):
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
