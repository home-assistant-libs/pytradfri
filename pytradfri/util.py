"""JSON utility functions."""
#  https://github.com/home-assistant/home-assistant/blob/4e8723f345d526ffbcbea74444e1a140a7eec863/homeassistant/util/json.py

import logging
from typing import Union, List, Dict
from .error import PytradfriError
import json

_LOGGER = logging.getLogger(__name__)


def load_json(filename: str) -> Union[List, Dict]:
    """Load JSON data from a file and return as dict or list.

    Defaults to returning empty dict if file is not found.
    """
    try:
        with open(filename, encoding='utf-8') as fdesc:
            return json.loads(fdesc.read())
    except FileNotFoundError:
        # This is not a fatal error
        _LOGGER.debug('JSON file not found: %s', filename)
    except ValueError as error:
        _LOGGER.exception('Could not parse JSON content: %s', filename)
        raise PytradfriError(error)
    except OSError as error:
        _LOGGER.exception('JSON file reading failed: %s', filename)
        raise PytradfriError(error)
    return {}  # (also evaluates to False)


def save_json(filename: str, config: Union[List, Dict]):
    """Save JSON data to a file.

    Returns True on success.
    """
    try:
        data = json.dumps(config, sort_keys=True, indent=4)
        with open(filename, 'w', encoding='utf-8') as fdesc:
            fdesc.write(data)
            return True
    except TypeError as error:
        _LOGGER.exception('Failed to serialize to JSON: %s',
                          filename)
        raise PytradfriError(error)
    except OSError as error:
        _LOGGER.exception('Saving JSON file failed: %s',
                          filename)
        raise PytradfriError(error)
    return False
