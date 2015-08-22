"""Views for game players."""
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.json_response import json_response
from planningpoker.persistence.exceptions import (
    NoSuchGame, PlayerNameTaken, PlayerAlreadyRegistered,
)
from planningpoker.views.identity import get_or_assign_id


@route('POST', '/game/{game_id}/join')
def join_game(request, persistence):
    """Join a game and provide a name."""
    game_id = request.match_info['game_id']
    try:
        player_name = (yield from request.post())['name']
    except KeyError:
        return json_response({'error': 'Must provide a name.'}, status=400)

    if len(player_name) < 1:
        return json_response({'error': 'The name must not be empty.'}, status=400)

    player_session = yield from get_session(request)
    player_id = get_or_assign_id(player_session)

    try:
        persistence.add_player(game_id, player_id, player_name)
    except NoSuchGame:
        return json_response({'error': 'There is no such game.'}, status=404)
    except PlayerNameTaken:
        return json_response({'error': 'There is already a player with such name in the game.'},
                             status=409)
    except PlayerAlreadyRegistered:
        return json_response({'error': 'The client is already registered in this game.'},
                             status=409)

    return json_response({'game': persistence.serialize_game(game_id)})


@route('POST', '/game/{game_id}/round/{round_name}/vote')
def cast_vote(request, persistence):
    """Vote in a poll."""
