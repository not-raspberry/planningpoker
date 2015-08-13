"""Persistence backend exceptions."""


class PersistenceError(Exception):

    """Base exception class for all persistence backends' errors."""


class ObjectNotFound(PersistenceError):

    """Base for exceptions raised when something should have been found but wasn't."""


class NameCollision(PersistenceError):

    """Base for exceptions raised when some name already exists."""


class InvalidState(PersistenceError):

    """Base for exceptions raised when attempting to alter an object of invalid state."""


class GameExists(NameCollision):

    """Raised if there is a game ID collision."""


class NoSuchGame(ObjectNotFound):

    """Raised if a game was not found."""


class RoundExists(NameCollision):

    """Raised if there is a round name collision within a game."""


class NoSuchRound(ObjectNotFound):

    """Raised if a round was not found within a game."""


class NoActivePoll(ObjectNotFound):

    """Raised if there is no active poll within a round."""


class RoundFinalized(InvalidState):

    """Raised when trying to add a new poll to a round that has already been finalized."""


class IllegalEstimation(PersistenceError):

    """Raised when the estimation a player votes for is not allowed in this game."""
