"""Command implementation."""


class Command(object):
    """The object for coap commands."""
    def __init__(self, method, path, data=None, *, parse_json=True, timeout=10,
                 observe=False, observe_duration=0, callback=None):
        self._method = method
        self._path = path
        self._data = data
        self._parse_json = parse_json
        self._timeout = timeout
        self._callback = callback
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
    def timeout(self):
        return self._timeout

    @property
    def callback(self):
        return self._callback

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
        if self._callback:
            self._result = self._callback(value)

        self._raw_result = value

    def url(self, host):
        """Generate url for coap client."""
        path = '/'.join(str(v) for v in self._path)
        return 'coaps://{}:5684/{}'.format(host, path)
