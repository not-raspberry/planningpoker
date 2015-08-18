"""Application status."""
from aiohttp import web

from planningpoker.routing import route


@route('GET', '/status')
def get_status(request, persistence):
    """Respond with OK and the number of games in response body."""
    return web.Response(body='{}\n'.format(persistence.games_count).encode('utf-8'))