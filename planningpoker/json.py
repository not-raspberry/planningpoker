"""JSON request and response response helpers."""
from decimal import Decimal
from functools import partial

from aiohttp.web import json_response as original_json_response
import simplejson


def dump_to_json(data: (dict, list, int, float, Decimal, str, None)) -> str:
    """
    Dump JSON-serializable data to JSON.

    Annoyances this function aviods:
        - stdlib ``json`` cannot dump Decimals
        - unicode characters are normally unnecessarily escaped

    :return: bytes with JSON that may contain unescaped (in JSON domain) unicode characters
    """
    return simplejson.dumps(data, ensure_ascii=False)


json_response = partial(original_json_response, dumps=dump_to_json)


def loads_or_empty(text: str) -> (dict, list, int, float, str, None):
    """
    Try to parse the text as JSON and return an empty dict if it fails.

    :raise: HTTPBadRequest if ``text`` is not JSON
    """
    try:
        return simplejson.loads(text)
    except simplejson.JSONDecodeError:
        return {}
