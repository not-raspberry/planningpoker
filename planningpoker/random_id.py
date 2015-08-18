"""
Random ID generation.

Mind that we cannot use ``uuid.uuid4`` because RFC 4122 does not define UUID4 to be securely
random. Python and Linux implementations (which Python falls back to) do the right thing but we
shouldn't rely on that.
"""
import os
import types
from binascii import hexlify


def get_random_id(length: int = 16, urandom: types.FunctionType = os.urandom) -> str:
    """
    Get ``length`` bytes of system random as hexadecimal string.

    :param length: number of bytes to get from `urandom`
    :param urandom: function that takes an integer and returns system random bytes of length equal
        to the integer passed to it
    """
    return hexlify(urandom(length)).decode()
