"""Testing random id generation."""
from binascii import unhexlify

import pytest

from planningpoker.random_id import get_random_id


def test_get_random_id_unhexlify():
    """Check if ``get_random_id`` encodes urandom bytes to hex properly."""
    urandom_sample = b'123442111'
    random_id = get_random_id(urandom=lambda _: urandom_sample)
    assert unhexlify(random_id) == urandom_sample


@pytest.mark.parametrize('length', range(1, 100, 13))
def test_get_random_id_urandom_length(length):
    """Check if get_random_id reads only ``length`` bytes."""
    random_id = get_random_id(length=length)
    assert len(unhexlify(random_id)) == length
