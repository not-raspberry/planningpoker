"""Persistence backend exceptions."""


class PersistenceError(Exception):

    """
    Base exception class for all persistence backends' errors.

    Because multiple presistence backends are required to raise the same exceptions and the
    exceptions are fine-grained, the error messages are parts of exception classes.
    """

    message = NotImplemented

    def __str__(self):
        """String representation."""
        return self.message.format(s=self)


class GameError(PersistenceError):

    """Base for game exceptions."""

    def __init__(self, game_id: str):
        """
        Store the game ID.

        :param game: game ID
        """
        self.game_id = game_id


class RoundError(PersistenceError):

    """Base for round exceptions."""

    message = NotImplemented

    def __init__(self, game_id: str, round_name: str):
        """
        Store the round name and game ID.

        :param game: game ID
        :param round: round name
        """
        self.game_id = game_id
        self.round_name = round_name


class PlayerError(PersistenceError):

    """Base for player errors."""

    message = NotImplemented

    def __init__(self, game_id: str, player_name: str):
        """
        Store the round name and the player name.

        :param game: game ID
        :param player_id: conflicting player id
        :param player_name: conflicting player name
        """
        self.game_id = game_id
        self.player_name = player_name


class GameExists(GameError):

    """Raised if there is a game ID collision."""

    message = "The game with ID '{s.game_id}' already exists."


class NoSuchGame(GameError):

    """Raised if a game was not found."""

    message = 'The game with ID {s.game_id} does not exist.'


class RoundExists(RoundError):

    """Raised if there is a round name collision within a game."""

    message = 'The round {s.round_name} already exists in the game {s.game_id}.'


class NoSuchRound(RoundError):

    """Raised if a round was not found within a game."""

    message = 'The round with name {s.round_name} was not found in the game {s.game_id}.'


class NoActivePoll(RoundError):

    """Raised if there is no active poll within a round."""

    message = 'The round {s.round_name} of the game {s.game_id} has no active poll.'


class RoundFinalized(RoundError):

    """Raised when trying to add a new poll to a round that has already been finalized."""

    message = 'The round {s.round_name} of the game {s.game_id} has already been finalized.'


class IllegalEstimation(PersistenceError):

    """Raised when the estimation a player votes for is not allowed in this game."""

    message = 'The estimation {s.estimation} is not available in the game {s.game_id}.'

    def __init__(self, game_id: str, estimation: str):
        """
        Store the round name and the estimation.

        :param game: game ID
        :param estimation: choosen invalid estimation
        """
        self.game_id = game_id
        self.estimation = estimation


class PlayerNameTaken(PlayerError):

    """Raised when there is a player name conflict in a game."""

    message = "There is already a player with the name {s.player_name} in the game {s.game_id}."


class PlayerAlreadyRegistered(PlayerError):

    """Raised when a player is already registered in a game."""

    message = 'The player is already registered in the game {s.game_id} as {s.player_name}.'
