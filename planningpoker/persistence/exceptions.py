"""Persistence backend exceptions."""


class PersistenceError(Exception):

    """Base exception class for all persistence backends' errors."""


class GameExists(PersistenceError):

    """Raised if there is a game ID collision."""


class NoSuchGame(PersistenceError):

    """Raised if a game was not found."""


class NoSuchRound(PersistenceError):

    """Raised if a round was not found within a game."""


class NoActivePoll(PersistenceError):

    """Raised if there is no active poll within a round."""
