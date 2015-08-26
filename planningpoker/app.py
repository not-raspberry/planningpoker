#!/usr/bin/env python3
"""Web app initialization."""
import sys
from functools import wraps

import click
from simplejson import load, JSONDecodeError
import asyncio
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from planningpoker.routing import routes
from planningpoker.persistence import BasePersistence, ProcessMemoryPersistence


@asyncio.coroutine
def init(loop, host: str, port: int, secret_key: str, persistence: BasePersistence):
    """Initialize the application."""
    app = web.Application(
        loop=loop,
        middlewares=[session_middleware(EncryptedCookieStorage(secret_key))]
    )

    for name, (method, path, handler) in routes.items():

        def add_persistence_to_handler(handler):
            @asyncio.coroutine
            @wraps(handler)
            def handler_with_persistence(*args, **kwargs):
                return handler(*args, persistence=persistence, **kwargs)

            return handler_with_persistence

        app.router.add_route(
            method, path, add_persistence_to_handler(handler), name=name)

    srv = yield from loop.create_server(app.make_handler(), host, port)
    print('HTTP server started at %s:%s' % (host, port), file=sys.stderr)
    return srv


@click.command()
@click.option('-H', '--host', type=str, help='Host for the web app to bind to.')
@click.option('-p', '--port', type=int, help='Port for the web app to listen on.')
@click.option('-k', '--cookie-secret-key', type=str,
              help='Key to encrypt the cookies with. Key length must be a multiple of 16.')
@click.option('-c', '--config', 'config_file', type=click.File('r'),
              help='Config file to fall back to if options are not provided.')
def cli_entry(host, port, cookie_secret_key, config_file):
    """
    Run the planningpoker web application.

    The JSON config file has the same keys as full options, except for the leading hyphens.
    """
    if config_file is None:
        if host is None or port is None or cookie_secret_key is None:
            print('When no config is provided, all options must be passed.', file=sys.stderr)
            exit(1)
    else:
        try:
            config = load(config_file)
        except JSONDecodeError as e:
            print('The config file must be valid JSON. Error: %r' % e, file=sys.stderr)
            exit(1)

    try:
        if host is None:
            host = config['host']
        if port is None:
            port = config['port']
        if cookie_secret_key is None:
            cookie_secret_key = config['cookie_secret_key']
    except KeyError as e:
        [key] = e.args
        print('Key not found in config: %r' % key, file=sys.stderr)
        exit(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(
        loop,
        host, port, cookie_secret_key,
        persistence=ProcessMemoryPersistence()
    ))
    loop.run_forever()
