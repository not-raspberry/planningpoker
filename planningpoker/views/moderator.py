"""Views for the game moderator."""
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.random_id import get_random_id
from planningpoker.json_response import json_response


@route('POST', '/new_game')
def add_game(request, persistence):
    """
    Create a new game.

    The user will become the moderator of the game.
    """
    try:
        available_cards = (yield from request.post()).getall('cards')
    except KeyError:
        return json_response({'error': 'No card set provided.'}, status=400)

    game_id = get_random_id()
    persistence.add_game(game_id, available_cards)

    moderator_session = yield from get_session(request)
    users_games = moderator_session.setdefault('games', [])
    users_games.append(game_id)

    return json_response({'game_id': game_id})
