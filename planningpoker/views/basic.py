"""A silly view."""
import asyncio
from aiohttp import web

from planningpoker.routing import route


@route('GET', '/')
@asyncio.coroutine
def handle(request):
    """Really silly."""
    return web.Response(body='Responding\n'.encode('utf-8'))
