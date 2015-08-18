"""Test ``json_response`` helper."""
import pytest

from planningpoker.json_response import json_response


@pytest.mark.parametrize('native_data, resulting_bytes', [
    (None, b'null'),
    ({}, b'{}'),
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
