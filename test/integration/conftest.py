"""Integration testing fixures."""
from urllib.parse import urlencode, urlunsplit

import pytest
from requests import Session
from mirakuru import HTTPExecutor

from planningpoker.settings import HOST, PORT


SITE_SCHEME = 'http'
SITE_NETLOC = '%s:%s' % (HOST, PORT)
SITE_ADDRESS = '%s://%s' % (SITE_SCHEME, SITE_NETLOC)
EXECUTOR_TIMEOUT = 5


class BackendSession(Session):

    """
    A session with requests methods accepting URL fragments, not URL strings.

    We abuse the ``url`` and keyword args that ``Session`` passes to the ``request`` method.
    Session's ``url`` becomes the ``path`` in the ``request`` method below and keyword arguments
    ``query`` and ``fragment`` are passed from other methods (``Session.get``, ``Session.put``)
    as keyword args.
    """

    def __init__(self, scheme: str, netloc: str, *args, **kwargs):
        """
        Store base address.

        :param scheme: URL scheme, like 'http'
        :param netloc: URL netloc, e.g 'example.com:80' in 'http://example.com:80'
        """
        self.scheme = scheme
        self.netloc = netloc
        super().__init__(*args, **kwargs)

    def request(self,
                method: str,
                path: str,
                query: (dict, None)=None,
                fragment: str='',
                *args, **kwargs):
        """
        Construct a URL and send a request.

        :param method: HTTP method to use, as in the supermethod
        :param path: URL path to use
        :param query: dict to form the query string from (lists as values will generate individual
            key=value pairs)
        :param fragment: the part of the URL after the hash
        """
        if query is None:
            query = {}

        qs = urlencode(query, doseq=True)
        url = urlunsplit((self.scheme, self.netloc, path, qs, fragment))
        return super().request(method, url, *args, **kwargs)


@pytest.fixture
def backend(request):
    """Run application backend."""
    executor = HTTPExecutor(
        ['./planningpoker/app.py'],
        SITE_ADDRESS + '/status',
        timeout=EXECUTOR_TIMEOUT
    )
    executor.start()
    request.addfinalizer(executor.stop)


@pytest.fixture
def client(backend):
    """Return a client session."""
    session = BackendSession(SITE_SCHEME, SITE_NETLOC)
    return session
