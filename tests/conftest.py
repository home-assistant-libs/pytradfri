import pytest


class MockApi:
    def __init__(self):
        self.mocks = {}
        self.calls = []

    def mock_request(self, method, path, response):
        key = (method, tuple(path))
        self.mocks[key] = response

    def __call__(self, method, path, data=None):
        self.calls.append({
            'method': method,
            'path': path,
            'data': data
        })

        key = (method, tuple(path))
        return self.mocks.get(key)


@pytest.fixture
def mock_api():
    """Mock coap api."""
    return MockApi()
