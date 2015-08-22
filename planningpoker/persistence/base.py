"""Base for persistence backends."""
import abc


class BasePersistence(abc.ABC):

    """Base persistence backend."""

    @property
    @abc.abstractmethod
    def games_count(self) -> int:
        """Return games count."""

    @abc.abstractmethod
    def add_game(self, game_id, cards: list) -> None:
        """
        Register a game.

        :param game_id: game's unique ID
        :param cards: a list of possible estimations in this game
        :raise GameExists: if a game with such ID already exists
        """

    @abc.abstractmethod
    def add_player(self, game_id, player_name: str) -> None:
        """
        Register a player in a game.

        :param game_id: game's unique ID
        :param cards: a list of possible estimations in this game
        :raise NoSuchGame: if there is no game with such ID
        :raise PlayerExists: if there is already a player with such name in the game
        """

    @abc.abstractmethod
    def add_round(self, game_id: str, round_name: str) -> None:
        """
        Add next round to a game.

        :param game_id: existing game's unique ID
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        :raise RoundExists: if there is already a round with such name in the game
        """

    @abc.abstractmethod
    def add_poll(self, game_id: str, round_name: str) -> None:
        """
        Create a poll where players can cast votes.

        The poll can be later accepted or rejected.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the round to add a poll to
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise RoundFinalized: if the round has already been finalized
        """

    @abc.abstractmethod
    def finalize_round(self, game_id: str, round_name: str) -> None:
        """
        Accept the current poll and finalize the round.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the round to finalize
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        :raise RoundFinalized: if the round has already been finalized
        """

    @abc.abstractmethod
    def cast_vote(self, game_id: str, round_name: str, voter_name: str, estimation: str) -> None:
        """
        Cast a vote for the current poll.

        The vote can be changed until the end of the poll.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :param voter_name: name of the voter
        :param estimation: the estimation the voter votes for
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        :raise RoundFinalized: if the round has already been finalized
        :raise IllegalEstimation: if the voter voted for a card that doesn't take a part in the game
        """

    @abc.abstractmethod
    def serialize_game(self, game_id: str) -> dict:
        """
        Fetch and serialize all game's data to a dict.

        :return: a dict loselessly serializable to JSON
        :raise NoSuchGame: if there is no game with such ID
        """
