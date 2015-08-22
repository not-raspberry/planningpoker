"""Views for the game moderator."""
from decimal import Decimal, InvalidOperation
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.random_id import get_random_id
from planningpoker.json_response import json_response
from planningpoker.persistence.exceptions import RoundExists


def coerce_cards(cards: list) -> list:
    """Cast strings in a list to Decimal if they are numeric, otherwise leave them as strings."""
    cast_cards = []
    for card in cards:
        try:
            cast_card = Decimal(card)
        except InvalidOperation:
            cast_card = card

        cast_cards.append(cast_card)

    return cast_cards


def client_owns_game(game_id, session):
    """Return True if the user who owns the session is the moderator of the game."""
    return game_id in session.get('games', [])


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
    if len(available_cards) < 2:
        return json_response({'error': 'Cannot play with less than 2 cards.'}, status=400)

    game_id = get_random_id()
    persistence.add_game(game_id, coerce_cards(available_cards))

    moderator_session = yield from get_session(request)
    users_games = moderator_session.setdefault('games', [])
    users_games.append(game_id)

    return json_response({'game_id': game_id, 'game': persistence.serialize_game(game_id)})


@route('POST', '/game/{game_id}/new_round')
def add_round(request, persistence):
    """Add a round to the game."""
    game_id = request.match_info['game_id']
    try:
        round_name = (yield from request.post())['round_name']
    except KeyError:
        return json_response({'error': 'Must specify the name.'}, status=400)

    if len(round_name) < 1:
        return json_response({'error': 'The name must not be empty.'}, status=400)

    user_session = yield from get_session(request)
    if not client_owns_game(game_id, user_session):
        return json_response({'error': 'The user is not the moderator of this game.'}, status=403)

    try:
        persistence.add_round(game_id, round_name)
    except RoundExists:
        return json_response({'error': 'Round with this name already exists.'}, status=409)
    # No point to catch NoSuchGame because we cannot sensibly handle situation when there is a game
    # in a session but not in the storage. Let's better 500.

    return json_response({'game': persistence.serialize_game(game_id)})
