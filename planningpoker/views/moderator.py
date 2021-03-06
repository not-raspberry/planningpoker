"""Views for the game moderator."""
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.random_id import get_random_id
from planningpoker.json import json_response, loads_or_empty
from planningpoker.cards import coerce_cards
from planningpoker.persistence.exceptions import (
    RoundExists, NoSuchRound, RoundFinalized, NoActivePoll
)
from planningpoker.views.identity import client_owns_game, get_or_assign_id


@route('POST', '/new_game')
async def add_game(request, persistence):
    """
    Create a new game.

    The user will become the moderator of the game.
    """
    json = await request.json(loads=loads_or_empty)

    try:
        available_cards = json['cards']
    except KeyError:
        return json_response({'error': 'No card set provided.'}, status=400)

    moderator_name = json.get('moderator_name', '')
    if moderator_name == '':
        return json_response({'error': 'Moderator name not provided.'}, status=400)

    if len(available_cards) < 2:
        return json_response({'error': 'Cannot play with less than 2 cards.'}, status=400)

    moderator_session = await get_session(request)
    # Get or assign the moderator id:
    moderator_id = get_or_assign_id(moderator_session)
    game_id = get_random_id()
    persistence.add_game(game_id, moderator_id, moderator_name, coerce_cards(available_cards))

    return json_response({'game_id': game_id, 'game': persistence.serialize_game(game_id)})


@route('POST', '/game/{game_id}/new_round')
async def add_round(request, persistence):
    """Add a round to the game."""
    game_id = request.match_info['game_id']
    json = await request.json(loads=loads_or_empty)

    try:
        round_name = json['round_name']
    except KeyError:
        return json_response({'error': 'Must specify the name.'}, status=400)

    if len(round_name) < 1:
        return json_response({'error': 'The name must not be empty.'}, status=400)

    user_session = await get_session(request)
    if not client_owns_game(game_id, user_session, persistence):
        return json_response({'error': 'The user is not the moderator of this game.'}, status=403)

    try:
        persistence.add_round(game_id, round_name)
    except RoundExists:
        return json_response({'error': 'Round with this name already exists.'}, status=409)
    # No point to catch NoSuchGame because we cannot sensibly handle situation when there is a game
    # in a session but not in the storage. Let's better 500.

    return json_response({'game': persistence.serialize_game(game_id)})


@route('POST', '/game/{game_id}/round/{round_name}/new_poll')
async def add_poll(request, persistence):
    """Add a poll to a round."""
    game_id = request.match_info['game_id']
    round_name = request.match_info['round_name']
    user_session = await get_session(request)

    if not client_owns_game(game_id, user_session, persistence):
        return json_response({'error': 'The user is not the moderator of this game.'}, status=403)

    try:
        persistence.add_poll(game_id, round_name)
    except NoSuchRound:
        return json_response({'error': 'Round does not exist.'}, status=404)
    except RoundFinalized:
        return json_response({'error': 'This round is finalized.'}, status=409)

    return json_response({'game': persistence.serialize_game(game_id)})


@route('POST', '/game/{game_id}/round/{round_name}/finalize')
async def finalize_round(request, persistence):
    """Finalize an owned round."""
    game_id = request.match_info['game_id']
    round_name = request.match_info['round_name']
    user_session = await get_session(request)

    if not client_owns_game(game_id, user_session, persistence):
        return json_response({'error': 'The user is not the moderator of this game.'}, status=403)

    try:
        persistence.finalize_round(game_id, round_name)
    except NoSuchRound:
        return json_response({'error': 'Round does not exist.'}, status=404)
    except NoActivePoll:
        return json_response({'error': 'There is no active poll in this round.'}, status=404)
    except RoundFinalized:
        return json_response({'error': 'This round has already been finalized.'}, status=409)

    return json_response({'game': persistence.serialize_game(game_id)})
