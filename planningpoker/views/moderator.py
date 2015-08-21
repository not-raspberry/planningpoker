"""Views for the game moderator."""
from decimal import Decimal, InvalidOperation
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.random_id import get_random_id
from planningpoker.json_response import json_response


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
