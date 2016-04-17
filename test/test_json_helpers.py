"""Test ``planningpoker.json`` helpers."""
from decimal import Decimal

import pytest

from planningpoker.json import json_response, loads_or_empty


@pytest.mark.parametrize('native_data, resulting_bytes', [
    (None, b'null'),
    ({}, b'{}'),
    ({'a': Decimal(10)}, b'{"a": 10}'),
    ({'a': Decimal('10.0')}, b'{"a": 10.0}'),
    ('łąż', '"łąż"'.encode()),
    (1, b'1'),
    ({'óóśś': 12}, '{"óóśś": 12}'.encode()),
])
def test_json_response_encoding(native_data, resulting_bytes):
    """Check if ``json_response`` encodes compatible Python data structures to JSON bytes."""
    response = json_response(native_data)
    assert isinstance(response.body, bytes)
    assert response.body == resulting_bytes


def test_json_response_argument_passing():
    """Check if ``json_response`` passes keyword args to ``aiohttp.web.Response``."""
    status = 400
    reason = 'I have a bad day'

    response = json_response({'food': 'tortilla'}, status=status, reason=reason)
    assert response.status == status
    assert response.reason == reason


@pytest.mark.parametrize('text, loaded', [
    ('', {}),
    ('{}', {}),
    ('{', {}),
    ('a', {}),
    ('😸', {}),
    ('ąśðł', {}),
    ('"😸"', "😸"),
    ('null', None),
    ('{"a": 12}', {'a': 12}),
    ('[]', []),
])
def test_loads_or_empty(text, loaded):
    """Test if ``loads_or_empty`` returns an empty dict for invalid payloads."""
    assert loads_or_empty(text) == loaded
