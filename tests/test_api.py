"""Test API utilities."""
import pytest

from pytradfri import retry_timeout, RequestTimeout


def test_retry_timeout_passes_args():
    """Test passing args."""
    calls = []

    def api(*args, **kwargs):
        """Mock api"""
        calls.append((args, kwargs))

    retry_api = retry_timeout(api)

    retry_api(1, 2, hello='world')
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == (1, 2)
    assert kwargs == {'hello': 'world'}


def test_retry_timeout_retries_timeouts():
    """Test retrying timeout."""
    calls = []

    def api(*args, **kwargs):
        """Mock api"""
        calls.append((args, kwargs))

        if len(calls) == 1:
            raise RequestTimeout()

    retry_api = retry_timeout(api, retries=2)

    retry_api(1, 2, hello='world')
    assert len(calls) == 2


def test_retry_timeout_raises_after_max_retries():
    """Test retrying timeout."""
    calls = []

    def api(*args, **kwargs):
        """Mock api"""
        calls.append((args, kwargs))

        raise RequestTimeout()

    retry_api = retry_timeout(api, retries=5)

    with pytest.raises(RequestTimeout):
        retry_api(1, 2, hello='world')

    assert len(calls) == 5
