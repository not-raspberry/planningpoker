"""Views for game players."""
from aiohttp_session import get_session

from planningpoker.routing import route
from planningpoker.json_response import json_response
from planningpoker.cards import coerce_card
from planningpoker.persistence.exceptions import (
    NoSuchGame, NoSuchRound, RoundFinalized, PlayerNameTaken, PlayerAlreadyRegistered,
    PlayerNotInGame, IllegalEstimation
)
from planningpoker.views.identity import get_or_assign_id, get_id


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
    """Vote in the active poll in the round."""
    game_id = request.match_info['game_id']
    round_name = request.match_info['round_name']
    player_session = yield from get_session(request)
    player_id = get_id(player_session)
    vote = coerce_card((yield from request.post())['vote'])

    try:
        persistence.cast_vote(game_id, round_name, player_id, vote)
    except NoSuchGame:
        return json_response({'error': 'There is no such game.'}, status=404)
    except NoSuchRound:
        return json_response({'error': 'There is no such round in the game.'}, status=404)
    except RoundFinalized:
        return json_response({'error': 'The round is finalized.'}, status=409)
    except IllegalEstimation:
        return json_response({'error': 'The estimation voted for is invalid.'}, status=400)
    except PlayerNotInGame:
        return json_response({'error': 'Cannot vote until the name is provided.'}, status=401)

    return json_response({'game': persistence.serialize_game(game_id)})
