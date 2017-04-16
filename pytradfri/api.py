"""API utilities."""

from .error import RequestTimeout


def retry_timeout(api, retries=3):
    """Retry API call when a timeout occurs."""
    def retry_api(*args, **kwargs):
        """Retrying API."""
        for i in range(1, retries + 1):
            try:
                return api(*args, **kwargs)
            except RequestTimeout:
                if i == retries:
                    raise

    return retry_api
