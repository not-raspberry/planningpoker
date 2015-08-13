"""In-memory persistence backend implementation."""
from planningpoker.persistence.base import BasePersistence
from planningpoker.persistence.exceptions import (
    GameExists, RoundExists, NoSuchGame, NoSuchRound, NoActivePoll, RoundFinalized,
    IllegalEstimation
)


class ProcessMemoryPersistence(BasePersistence):

    """
    'Persistence' backed by process memory.

    Able to persist between requests. All data will be lost when the process
    exits.

    Not thread-safe.

    The complete state is kept in the `self.games` dict.

    Schema:
        self.games = {
            '<game-id>': {  # Game dict.
                'cards': [1, 3, 5, 8, 13, ...],  # A list of possible estimations.
                'rounds_order': ['<name-of-the-first-round>', ...],  # Rounds in order.
                'rounds': {
                    '<name-of-the-first-round>': {  # A round object.
                        'polls': [  # List of polls in the round.
                            {  # Results of a poll.
                                '<player-1>': 40,
                                '<player-3>': 13,
                                ...
                            },
                            ...
                        ],
                        'finalized': False,  # True means no more polls can be added and the
                                             # result of the last poll is the result of the
                                             # round.
                    ...
                }
            }
            ...
        }

    We don't use OrderedDicts to keep JSON serialization trivial.
    """

    def __init__(self):
        """Instantiate the memory persistence with no games."""
        self.games = {}

    def _get_game(self, game_id: str) -> None:
        """
        Find a game.

        :param game_id: existing game's unique ID
        :raise NoSuchGame: if there is no game with such ID
        """
        try:
            return self.games[game_id]
        except KeyError:
            raise NoSuchGame('The game with ID %r does not exist.' % game_id)

    def _get_round(self, game_id: str, round_name: str, ensure_active: bool = False) -> None:
        """
        Find a round.

        :param game_id: existing game's unique ID
        :param round_name: user-provided name of the round to get
        :param ensure_active: if True, ensure the round is not finalized
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise RoundFinalized: if the round has already been finalized and `ensure_active` is True
        """
        try:
            round = self._get_game(game_id)['rounds'][round_name]
        except KeyError:
            raise NoSuchRound('The round with name %r was not found' % round_name)

        if ensure_active and round['finalized'] is True:
            raise RoundFinalized('The round %r of the game %r has already been finalized.'
                                 % (round_name, game_id))
        return round

    def add_game(self, game_id, cards: list) -> None:
        """
        Register a game.

        Insert into the games dict a key of the new game ID with the value of the new game dict.

        :param game_id: game's unique ID
        :param cards: a list of possible estimations in this game
        :raise GameExists: if a game with such ID already exists
        """
        if game_id in self.games:
            raise GameExists('The game with ID %r already exists.' % game_id)

        self.games[game_id] = {
            'cards': cards,
            'rounds_order': [],
            'rounds': {},
        }

    def add_round(self, game_id: str, round_name: str) -> None:
        """
        Add next round to a game.

        If a round already exists, it will be memorized and rejected.

        :param game_id: existing game's unique ID
        :param round_name: user-provided name of the new round
        :raise NoSuchGame: if there is no game with such ID
        :raise RoundExists: if there is already a round with such name in the game
        """
        game = self._get_game(game_id)
        if round_name in game['rounds']:
            raise RoundExists('The round %r already exists in the game.' % game_id)

        game['rounds_order'].append(round_name)
        game['rounds'][round_name] = {
            'finalized': False,
            'polls': []
        }

    def add_poll(self, game_id: str, round_name: str) -> None:
        """
        Create a poll where players can cast votes.

        The poll can be later accepted.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the round to add a poll to
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise RoundFinalized: if the round has already been finalized
        """
        round = self._get_round(game_id, round_name, ensure_active=True)
        round['polls'].append({})

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
        round = self._get_round(game_id, round_name, ensure_active=True)
        if round['polls'] == []:
            raise NoActivePoll('The round %r of the game %r has no active poll.'
                               % (round_name, game_id))
        round['finalized'] = True

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
        round = self._get_round(game_id, round_name, ensure_active=True)
        try:
            latest_poll = round['polls'][-1]
        except IndexError:
            raise NoActivePoll('The round %r of the game %r has no active poll.'
                               % (round_name, game_id))

        game = self._get_game(game_id)
        if estimation not in game['cards']:
            raise IllegalEstimation('The estimation %r is not one of available estimations in '
                                    'this game.' % estimation)

        latest_poll[voter_name] = estimation

    def serialize_game(self, game_id: str) -> dict:
        """
        Fetch and serialize all game's data to a dict.

        :raise NoSuchGame: if there is no game with such ID
        :return: a dict loselessly serializable to JSON
        """
        return self._get_game(game_id)
