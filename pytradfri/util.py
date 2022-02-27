"""JSON utility functions."""
from __future__ import annotations

import json
import logging

from .error import PytradfriError

#  https://github.com/home-assistant/home-assistant/blob/4e8723f345d526ffbcbea74444e1a140a7eec863/homeassistant/util/json.py


_LOGGER = logging.getLogger(__name__)


def load_json(filename: str) -> list | dict:
    """Load JSON data from a file and return as dict or list.

    Defaults to returning empty dict if file is not found.
    """
    try:
        with open(filename, encoding="utf-8") as fdesc:
            return json.loads(fdesc.read())
    except FileNotFoundError:
        # This is not a fatal error
        _LOGGER.debug("JSON file not found: %s", filename)
    except ValueError as exc:
        _LOGGER.exception("Could not parse JSON content: %s", filename)
        raise PytradfriError(exc) from exc
    except OSError as exc:
        _LOGGER.exception("JSON file reading failed: %s", filename)
        raise PytradfriError(exc) from exc
    return {}  # (also evaluates to False)


def save_json(filename: str, config: list | dict) -> bool:
    """Save JSON data to a file.

    Returns True on success.
    """
    try:
        data = json.dumps(config, sort_keys=True, indent=4)
        with open(filename, "w", encoding="utf-8") as fdesc:
            fdesc.write(data)
            return True
    except TypeError as exc:
        _LOGGER.exception("Failed to serialize to JSON: %s", filename)
        raise PytradfriError(exc) from exc
    except OSError as exc:
        _LOGGER.exception("Saving JSON file failed: %s", filename)
        raise PytradfriError(exc) from exc


class BitChoices:
    """Helper class for bitwise dates.

    http://stackoverflow.com/questions/3663898/representing-a-multi-select-field-for-weekdays-in-a-django-model
    """

    def __init__(self, choices):
        """Initialize BitChoices class."""
        self._choices = []
        self._lookup = {}
        for index, (key, val) in enumerate(choices):
            index = 2 ** index
            self._choices.append((index, val))
            self._lookup[key] = index

    def __iter__(self):
        """Iterate over object."""
        return iter(self._choices)

    def __len__(self):
        """Len."""
        return len(self._choices)

    def __getattr__(self, attr):
        """Getattr."""
        try:
            return self._lookup[attr]
        except KeyError as exc:
            raise AttributeError(attr) from exc

    def get_selected_keys(self, selection):
        """Return a list of keys for the given selection."""
        return [k for k, b in self._lookup.items() if b & selection]

    def get_selected_values(self, selection):
        """Return a list of values for the given selection."""
        return [v for b, v in self._choices if b & selection]
