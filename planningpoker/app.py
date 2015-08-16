#!/usr/bin/env python3
"""Web app initialization."""
import sys

import asyncio
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from planningpoker import settings
from planningpoker.routing import routes


@asyncio.coroutine
def init(loop, host: str, port: int, secret_key: str):
    """Initialize the application."""
    app = web.Application(
        loop=loop,
        middlewares=[session_middleware(EncryptedCookieStorage(secret_key))]
    )

    print('Setting up routes: %s' % routes, file=sys.stderr)

    for name, (method, path, handler) in routes.items():
        app.router.add_route(method, path, handler, name=name)

    srv = yield from loop.create_server(app.make_handler(), host, port)
    print('HTTP server started at %s:%s' % (host, port), file=sys.stderr)
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, settings.HOST, settings.PORT, settings.COOKIE_SECRET_KEY))
    loop.run_forever()
