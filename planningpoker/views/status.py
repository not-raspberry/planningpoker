"""Application status."""
from aiohttp import web

from planningpoker.routing import route
from planningpoker.json_response import json_response


@route('HEAD', '/status')
def head_status(request, persistence):
    """Respond with OK."""
    return web.Response()


@route('GET', '/status')
def get_status(request, persistence):
    """Respond with OK and the number of games in response body."""
    return json_response({'games_count': persistence.games_count})
