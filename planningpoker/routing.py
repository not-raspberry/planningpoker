"""
Contains a decorator to memorize routes to later pass them to the application.

This way the views are not dependent on the app and the routes are registered close to the handles.
"""
import types
from collections import namedtuple

Route = namedtuple('Route', ['method', 'path', 'handler'])
routes = {}
method_paths = set()


def route(method, path, name: str = None, *,
          routes_dict=routes, method_path_set=method_paths) -> types.FunctionType:
    """Return a decorator to register a view."""
    def decorator(handler_fn: types.FunctionType):
        """
        Add a route to `routes_dict`.

        The decorator does not modify the function.

        :raise ValueError: if a route with such name or path exists
        """
        nonlocal name
        if name is None:
            name = handler_fn.__name__

        if name in routes_dict:
            raise ValueError('Route with name %r exists' % name)

        if (method, path) in method_path_set:
            raise ValueError('Route with path %r exists.' % ((method, path),))

        routes_dict[name] = Route(method, path, handler_fn)
        method_path_set.add((method, path))
        return handler_fn

    return decorator


# Import all views so they register:
from planningpoker import views  # noqa
