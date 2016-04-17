"""Integration testing fixures."""
from urllib.parse import urlencode, urlunsplit

import pytest
import port_for
from cryptography.fernet import Fernet
from requests import Session
from mirakuru import HTTPExecutor


HOST = '127.0.0.1'
PORT = port_for.select_random()
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
        [
            'planningpoker',
            '--host', '127.0.0.1',
            '--port', str(PORT),
            '--cookie-secret-key', Fernet.generate_key().decode()
        ],
        SITE_ADDRESS + '/status',
        timeout=EXECUTOR_TIMEOUT
    )
    executor.start()
    request.addfinalizer(executor.stop)


def make_client() -> BackendSession:
    """Return a client session, not owning any game nor registered as a player."""
    return BackendSession(SITE_SCHEME, SITE_NETLOC)


def make_player(game_id: str, player_name: str) -> BackendSession:
    """Create a backend session that belongs to a game."""
    player = make_client()
    join_game = player.post('/game/%s/join' % game_id, json={'name': player_name})
    assert join_game.ok
    return player


@pytest.fixture
def client(backend):
    """Inject ``backend`` dependency and delegate to ``make_client``."""
    return make_client()


@pytest.fixture
def another_client(backend):
    """Return a client session with separate identity from the ``client``."""
    return make_client()


@pytest.fixture
def game_cards():
    """Return cards used by the game created by the ``moderator``."""
    return [1, 2, 3, 5, 8, 13, '?', 'Break?']


@pytest.fixture
def moderator_name():
    """Return the name of the test game moderator."""
    return 'Hannah'


@pytest.fixture
def game(backend, game_cards, moderator_name):
    """
    Create a game.

    :return: game ID and game moderator session
    """
    moderator = client(backend)
    game = moderator.post('/new_game', json={
        'cards': game_cards,
        'moderator_name': moderator_name,
    })
    assert game.ok
    return game.json()['game_id'], moderator


@pytest.fixture
def game_id(game):
    """Return the ID of a game created by the ``moderator``."""
    game_id, _ = game
    return game_id


@pytest.fixture(params=['round', 'Round One', 'Round łąśðœ→ęóæą'])
def game_round(moderator, game_id, request):
    """Add a round to the test game."""
    round_name = request.param
    round_request = moderator.post('/game/%s/new_round' % game_id, json={'round_name': round_name})
    assert round_request.ok
    return round_name


@pytest.fixture
def game_poll(moderator, game_round, game_id, request):
    """Add a poll to the test game."""
    poll_request = moderator.post('/game/%s/round/%s/new_poll' % (game_id, game_round))
    assert poll_request.ok


@pytest.fixture
def moderator(game):
    """Return a game moderator session."""
    _, moderator = game
    return moderator


@pytest.fixture
def player_name():
    """Return player name."""
    return 'Martin'


@pytest.fixture
def player(game, game_id, player_name):
    """Return a client registered within a game."""
    return make_player(game_id, player_name)
