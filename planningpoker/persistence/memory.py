"""In-memory persistence backend implementation."""
from planningpoker.persistence.base import BasePersistence
from planningpoker.persistence.exceptions import (
    GameExists, RoundExists, NoSuchGame, NoSuchRound, NoActivePoll, RoundFinalized,
    IllegalEstimation, PlayerNameTaken, PlayerAlreadyRegistered, PlayerNotInGame,
)


class ProcessMemoryPersistence(BasePersistence):

    """
    'Persistence' backed by process memory.

    Able to persist between requests. All data will be lost when the process
    exits.

    Not thread-safe.

    The complete state is kept in the `self._games` dict.

    Schema:
        self._games = {
            '<game-id>': {  # Game dict.
                'players': {'123fd1d9da37c': 'Beatrice', ...},  # Map of player IDs to player name.
                                                                # Includes the moderator.
                'moderator_id': 'wqsqw123',  # ID of the game owner.
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
        self._games = {}

    def _get_game(self, game_id: str) -> None:
        """
        Find a game.

        :param game_id: existing game's unique ID
        :raise NoSuchGame: if there is no game with such ID
        """
        try:
            return self._games[game_id]
        except KeyError:
            raise NoSuchGame(game_id)

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
            raise NoSuchRound(game_id, round_name)

        if ensure_active and round['finalized'] is True:
            raise RoundFinalized(game_id, round_name)

        return round

    @property
    def games_count(self) -> int:
        """Return games count."""
        return len(self._games)

    def add_game(self, game_id: str, moderator_id: str, moderator_name: str, cards: list) -> None:
        """
        Register a game.

        Insert into the games dict a key of the new game ID with the value of the new game dict.

        :param game_id: game's unique ID
        :param moderator_id: the ID that identifies the game owner
        :param moderator_name: the name of the game moderator that the players will see
        :param cards: a list of possible estimations in this game
        :raise GameExists: if a game with such ID already exists
        """
        if game_id in self._games:
            raise GameExists(game_id)

        self._games[game_id] = {
            'players': {moderator_id: moderator_name},
            'moderator_id': moderator_id,
            'cards': cards,
            'rounds_order': [],
            'rounds': {},
        }

    def add_player(self, game_id, player_id: str, player_name: str) -> None:
        """
        Register a player in a game.

        :param game_id: game's unique ID to add a player to
        :param player_id: player's unique ID
        :param player_name: player's name to use in this game
        :raise NoSuchGame: if there is no game with given ID
        :raise PlayerNameTaken: if there is already a player with such name in the game
        :raise PlayerAlreadyRegistered: if the player already belongs to the game
        """
        game = self._get_game(game_id)

        # Players list cannot be a set because that wouldn't serialize to JSON easily.
        # After all, how many players are we going to have? Especially on deployments using
        # process memory to keep state.
        if player_id in game['players']:
            raise PlayerAlreadyRegistered(game_id, player_name)
        if player_name in game['players'].values():
            raise PlayerNameTaken(game_id, player_name)

        game['players'][player_id] = player_name

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
            raise RoundExists(game_id, round_name)

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
            raise NoActivePoll(game_id, round_name)
        round['finalized'] = True

    def cast_vote(self, game_id: str, round_name: str, voter_id: str, estimation: str) -> None:
        """
        Cast a vote for the current poll.

        The vote can be changed until the end of the poll.

        :param game_id: existing game's unique id
        :param round_name: user-provided name of the new round
        :param voter_id: ID of the voter (not to be disclosed)
        :param estimation: the estimation the voter votes for
        :raise NoSuchGame: if there is no game with such ID
        :raise NoSuchRound: if there is no round with such name within the game
        :raise NoActivePoll: if there no active poll in the round
        :raise RoundFinalized: if the round has already been finalized
        :raise IllegalEstimation: if the voter voted for a card that doesn't take a part in the game
        :raise PlayerNotInGame: if the voter ID does not map to any player
        """
        round = self._get_round(game_id, round_name, ensure_active=True)
        try:
            latest_poll = round['polls'][-1]
        except IndexError:
            raise NoActivePoll(game_id, round_name)

        game = self._get_game(game_id)
        if estimation not in game['cards']:
            raise IllegalEstimation(game_id, estimation)

        try:
            voter_name = game['players'][voter_id]
        except KeyError:
            raise PlayerNotInGame(game_id, voter_id)

        latest_poll[voter_name] = estimation

    def serialize_game(self, game_id: str) -> dict:
        """
        Fetch and serialize all game's data to a dict.

        :raise NoSuchGame: if there is no game with such ID
        :return: a dict loselessly serializable to JSON
        """
        game = self._get_game(game_id)
        return {
            'players': list(game['players'].values()),
            'cards': game['cards'],
            'rounds_order': game['rounds_order'],
            'rounds': game['rounds'],
        }

    def client_owns_game(self, game_id: str, client_id: str) -> bool:
        """
        Check if a client is the moderator of the game.

        :param game_id: unique ID of the game to check for ownership
        :param moderator_id: ID of the client
        :return: True if a client is the moderator of the game
        """
        game = self._get_game(game_id)
        return game['moderator_id'] == client_id
