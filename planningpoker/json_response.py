"""JSON response helper."""
import simplejson

from aiohttp.web import Response


def json_response(response_data: dict, *args, **kwargs) -> Response:
    """
    Dump a dict to JSON and put into ``aiohttp.web.Response``.

    ``args`` and ``kwargs`` will be passed to ``aiohttp.web.Response``

    :param response_data: JSON to respond with
    :return: bytes with JSON that may contain unescaped (in JSON domain) unicode characters
    """
    json_resp = simplejson.dumps(response_data, ensure_ascii=False).encode()
    return Response(body=json_resp, *args, **kwargs)
