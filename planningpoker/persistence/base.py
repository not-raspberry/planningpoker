"""Base for persistence backends."""
import abc


class BasePersistence(abc.ABC):

    """Base persistence backend."""

    @abc.abstractmethod
    def add_game(self, game_id, cards: list) -> None:
        """
        Register a game.

        :param game_id: game's unique ID
        :param cards: a list of possible estimations in this game
        :raise GameExists: if a game with such ID already exists
        """

    @abc.abstractmethod
    def add_round(self, game_id: str, round_name: str) -> None:
        """
        Add next round to a game.

        :param game_id: existing game's unique ID
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        """

    @abc.abstractmethod
    def add_poll(self, game_id: str, round_name: str) -> None:
        """
        Create a poll where players can cast votes.

        The poll can be later accepted or rejected.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        """

    @abc.abstractmethod
    def accept_poll(self, game_id: str, round_name: str) -> None:
        """
        Accept the current poll and finalize the round.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        """

    @abc.abstractmethod
    def reject_poll(self, game_id: str, round_name: str) -> None:
        """
        Reject the current poll.

        A new poll can be created later.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        """

    @abc.abstractmethod
    def cast_vote(self, game_id: str, round_name: str, voter_name: str) -> None:
        """
        Cast a vote for the current poll.

        The vote can be changed until the end of the poll.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :param voter_name: name of the voter
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        """

    @abc.abstractmethod
    def serialize_game(self, game_id: str) -> dict:
        """
        Fetch and serialize all game's data to a dict.

        :raise NoSuchGame: if there is no game with such ID
        """
