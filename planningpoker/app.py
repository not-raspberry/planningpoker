#!/usr/bin/env python3
"""Web app initialization."""
import sys

import asyncio
from aiohttp import web

from planningpoker import settings
from planningpoker.routing import routes


@asyncio.coroutine
def init(loop, host: str, port: int):
    """Initialize the application."""
    app = web.Application(loop=loop)

    print('Setting up routes: %s' % routes, file=sys.stderr)

    for name, (method, path, handler) in routes.items():
        app.router.add_route(method, path, handler, name=name)

    srv = yield from loop.create_server(app.make_handler(), host, port)
    print('HTTP server started at %s:%s' % (host, port), file=sys.stderr)
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, settings.HOST, settings.PORT))
    loop.run_forever()
