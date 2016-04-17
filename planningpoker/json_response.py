"""JSON response helper."""
from decimal import Decimal
from functools import partial

from aiohttp.web import json_response as original_json_response
import simplejson


def dump_to_json(data: (dict, list, int, float, Decimal, str)) -> str:
    """
    Dump JSON-serializable data to JSON.

    Annoyances this function aviods:
        - stdlib ``json`` cannot dump Decimals
        - unicode characters are normally unnecessarily escaped

    :return: bytes with JSON that may contain unescaped (in JSON domain) unicode characters
    """
    return simplejson.dumps(data, ensure_ascii=False)


json_response = partial(original_json_response, dumps=dump_to_json)
