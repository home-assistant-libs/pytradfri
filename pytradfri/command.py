"""Command implementation."""

from copy import deepcopy


class Command(object):
    """The object for coap commands."""

    def __init__(self, method, path, data=None, *, parse_json=True,
                 observe=False, observe_duration=0, process_result=None,
                 err_callback=None):
        self._method = method
        self._path = path
        self._data = data
        self._parse_json = parse_json
        self._process_result = process_result
        self._err_callback = err_callback
        self._observe = observe
        self._observe_duration = observe_duration
        self._raw_result = None
        self._result = None

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        return self._data

    @property
    def parse_json(self):
        return self._parse_json

    @property
    def process_result(self):
        return self._process_result

    @property
    def err_callback(self):
        """This will be fired when an observe request fails."""
        return self._err_callback

    @property
    def observe(self):
        return self._observe

    @property
    def observe_duration(self):
        return self._observe_duration

    @property
    def raw_result(self):
        return self._raw_result

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        """The result of the command."""
        if self._process_result:
            self._result = self._process_result(value)

        self._raw_result = value

    def url(self, host):
        """Generate url for coap client."""
        path = '/'.join(str(v) for v in self._path)
        return 'coaps://{}:5684/{}'.format(host, path)

    def _merge(self, a, b):
        """Merges a into b."""
        for k, v in a.items():
            if isinstance(v, dict):
                item = b.setdefault(k, {})
                self._merge(v, item)
            elif isinstance(v, list):
                item = b.setdefault(k, [{}])
                if len(v) == 1 and isinstance(v[0], dict):
                    self._merge(v[0], item[0])
                else:
                    b[k] = v
            else:
                b[k] = v
        return b

    def combine_data(self, command2):
        """Combines the data for this command with another."""
        if command2 is None:
            return
        self._data = self._merge(command2._data, self._data)

    def __add__(self, other):
        if other is None:
            return deepcopy(self)
        if isinstance(other, self.__class__):
            newObj = deepcopy(self)
            newObj.combine_data(other)
            return newObj
        else:
            raise (TypeError("unsupported operand type(s) for +: "
                   "'{}' and '{}'".format(self.__class__, type(other))))
