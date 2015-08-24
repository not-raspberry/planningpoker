"""Track users' identities and permissions."""
from aiohttp_session import Session

from planningpoker.random_id import get_random_id
from planningpoker.persistence import BasePersistence

CLIENT_ID_KEY = 'client_id'


def client_owns_game(game_id: str, session: Session, persistence: BasePersistence) -> bool:
    """Return True if the user who owns the session is the moderator of the game."""
    try:
        client_id = session[CLIENT_ID_KEY]
    except KeyError:
        return False
    return persistence.client_owns_game(game_id, client_id)


def get_id(session: Session) -> (str, None):
    """Return client ID if it exists; else None."""
    return session.get(CLIENT_ID_KEY)


def get_or_assign_id(session: Session) -> str:
    """Return client's ID, and if it doesn't exist, assign it and return."""
    client_id = session.setdefault(CLIENT_ID_KEY, get_random_id())
    return client_id
