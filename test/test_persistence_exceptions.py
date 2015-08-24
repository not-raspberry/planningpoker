"""Check if the exceptions stringify well."""
from string import ascii_uppercase

import pytest

from planningpoker.persistence.exceptions import (
    GameError, RoundError, PlayerStateError,
    GameExists, RoundExists, NoSuchGame, NoSuchRound, NoActivePoll,
    RoundFinalized, IllegalEstimation, PlayerNameTaken, PlayerAlreadyRegistered,
    PlayerNotInGame
)


@pytest.mark.parametrize('exception_class', [
    GameExists, RoundExists, NoSuchGame, NoSuchRound, NoActivePoll, RoundFinalized,
    IllegalEstimation, PlayerNameTaken, PlayerAlreadyRegistered, PlayerNotInGame
])
def test_exceptions_stringification(exception_class):
    """Check exception __str__ formatting."""
    if issubclass(exception_class, GameError):
        args = ['game_id-1231231231']
    elif issubclass(exception_class, RoundError):
        args = ['game_id-1231231231', 'Round 40']
    elif issubclass(exception_class, IllegalEstimation):
        args = ['game_id-1231231231', 100]
    elif issubclass(exception_class, PlayerStateError):
        args = ['game_id-1231231231', 'Jerry']
    elif issubclass(exception_class, PlayerNotInGame):
        args = ['game_id-1231231231', '12312w21']

    exception = exception_class(*args)

    exception_message = str(exception)

    assert exception_message[0] in ascii_uppercase
    assert exception_message.endswith('.')

    for arg in args:
        assert str(arg) in exception_message
