"""Tests for persistence backends."""
import pytest

from planningpoker.persistence import ProcessMemoryPersistence
from planningpoker.persistence.exceptions import (
    GameExists, RoundExists, NoSuchGame, NoSuchRound, NoActivePoll, RoundFinalized,
    IllegalEstimation, PlayerNameTaken, PlayerAlreadyRegistered,
)

GAME_ID = 'game-123456'
GAME_CARDS = [1, 2, 3, 5, 8, 13]
MODERATOR_ID = 'asdfw1'
MODERATOR_NAME = 'Liz'
PLAYERS = ['mark', 'lisa', 'kim', 'george']
ROUND_NAME = 'Round One'


@pytest.fixture
def backend():
    """Create a persistence backend."""
    return ProcessMemoryPersistence()


@pytest.fixture
def backend_with_a_game(backend):
    """Return a persistence backend holding one game."""
    backend.add_game(GAME_ID, MODERATOR_ID, MODERATOR_NAME, GAME_CARDS)
    return backend


@pytest.fixture
def backend_with_a_round(backend_with_a_game):
    """Return a persistence backend holding one game with one round."""
    backend_with_a_game.add_round(GAME_ID, ROUND_NAME)
    return backend_with_a_game


@pytest.fixture
def backend_with_a_poll(backend_with_a_round):
    """Return a persistence backend holding one game with one round."""
    backend_with_a_round.add_poll(GAME_ID, ROUND_NAME)
    return backend_with_a_round


def test_initial_state(backend):
    """Check if the persistence backend is initially empty."""
    assert backend.games_count == 0


def test_add_game(backend):
    """Check adding a game and ID collision detection."""
    game_id = 'aaa'
    moderator_id = 'bbb'
    moderator_name = 'Rich'
    cards = [1, 2, 3, 4, 10]

    backend.add_game(game_id, moderator_id, moderator_name, cards)

    with pytest.raises(GameExists):
        backend.add_game(game_id, 'ddd', 'Frank', [2, 4, 6, 10])

    assert backend.games_count == 1
    assert backend.serialize_game(game_id) == {  # IDs not revealed.
        'players': [moderator_name],
        'cards': cards,
        'rounds_order': [],
        'rounds': {},
    }

    # It's possible for the same user to add a another game - with the same cards.
    another_game_id = 'qqq'
    backend.add_game(another_game_id, moderator_id, moderator_name, cards)
    assert backend.games_count == 2
    assert backend.serialize_game(game_id) == backend.serialize_game(another_game_id)

    assert backend.client_owns_game(game_id, moderator_id)
    assert backend.client_owns_game(another_game_id, moderator_id)
    assert not backend.client_owns_game(game_id, '12312-somebody-else')


def test_add_player(backend_with_a_game):
    """Check adding a player to a game and player name collisions."""
    backend = backend_with_a_game
    player_name = 'Gertrude'
    player_id = 'id-4411d'
    another_player_name = 'Marley'
    another_player_id = 'id-123sq'

    with pytest.raises(NoSuchGame):
        backend.add_player('nonexistent game', 'id-asdasd122', 'bob')

    backend.add_player(GAME_ID, player_id, player_name)

    with pytest.raises(PlayerAlreadyRegistered):
        backend.add_player(GAME_ID, player_id, player_name)

    with pytest.raises(PlayerAlreadyRegistered):
        # PlayerAlreadyRegistered is raised also when the player registers again with a different
        # name.
        backend.add_player(GAME_ID, player_id, 'another name')

    with pytest.raises(PlayerNameTaken):
        # Another player tries to register with the same name.
        backend.add_player(GAME_ID, 'another_player_id', player_name)

    players = backend.serialize_game(GAME_ID)['players']
    assert sorted(players) == sorted([MODERATOR_NAME, player_name])

    backend.add_player(GAME_ID, another_player_id, another_player_name)
    more_players = backend.serialize_game(GAME_ID)['players']
    assert sorted(more_players) == sorted([MODERATOR_NAME, player_name, another_player_name])


def test_add_round(backend_with_a_game):
    """Check adding a round and round name collision detection."""
    backend = backend_with_a_game
    round_name = 'round 1'

    with pytest.raises(NoSuchGame):
        backend.add_round('nonexistent game', round_name)

    backend.add_round(GAME_ID, round_name)

    with pytest.raises(RoundExists):
        backend.add_round(GAME_ID, round_name)

    serialized = backend.serialize_game(GAME_ID)
    assert serialized['rounds_order'] == [round_name]
    assert serialized['rounds'] == {round_name: {
        'polls': [],
        'finalized': False,
    }}

    another_round_name = 'round 2'
    backend.add_round(GAME_ID, another_round_name)
    serialized_2_rounds = backend.serialize_game(GAME_ID)
    assert serialized_2_rounds['rounds_order'] == [round_name, another_round_name]
    assert serialized_2_rounds['rounds'].keys() == {round_name, another_round_name}
    old_round = serialized['rounds'][round_name]
    assert serialized_2_rounds['rounds'][round_name] == old_round, 'The old one remained the same.'
    assert serialized_2_rounds['rounds'][another_round_name] == old_round, \
        'All rounds are created equal'


def test_add_poll(backend_with_a_round):
    """Test adding a poll."""
    backend = backend_with_a_round

    with pytest.raises(NoSuchGame):
        backend.add_poll('nonexistent_game', ROUND_NAME)

    with pytest.raises(NoSuchRound):
        backend.add_poll(GAME_ID, 'nonexistent_round')

    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == []

    backend.add_poll(GAME_ID, ROUND_NAME)
    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == [{}]

    backend.finalize_round(GAME_ID, ROUND_NAME)

    with pytest.raises(RoundFinalized):
        # It should not be possible to add a poll to a finalized round.
        backend.add_poll(GAME_ID, ROUND_NAME)


def test_finalize_round(backend_with_a_round):
    """Test finalizing a round."""
    backend = backend_with_a_round

    with pytest.raises(NoSuchGame):
        backend.finalize_round('nonexistent_game', ROUND_NAME)

    with pytest.raises(NoSuchRound):
        backend.finalize_round(GAME_ID, 'nonexistent_round')

    with pytest.raises(NoActivePoll):
        # It should not be possible to finalize a round with no polls.
        backend.finalize_round(GAME_ID, ROUND_NAME)

    backend.add_poll(GAME_ID, ROUND_NAME)

    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['finalized'] is False
    backend.finalize_round(GAME_ID, ROUND_NAME)
    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['finalized'] is True

    with pytest.raises(RoundFinalized):
        # It should not be possible to finalize the same round twice.
        backend.finalize_round(GAME_ID, ROUND_NAME)

    # It should still be possible to create another round.
    another_round_name = 'Another round!'
    backend.add_round(GAME_ID, another_round_name)
    backend.add_poll(GAME_ID, another_round_name)
    assert backend.serialize_game(GAME_ID)['rounds'][another_round_name]['finalized'] is False


def test_cast_vote(backend_with_a_round):
    """Test vote casting."""
    backend = backend_with_a_round

    with pytest.raises(NoSuchGame):
        backend.cast_vote('nonexistent_game', ROUND_NAME, 'bob', GAME_CARDS[0])

    with pytest.raises(NoSuchRound):
        backend.cast_vote(GAME_ID, 'nonexistent_round', 'alice', GAME_CARDS[0])

    with pytest.raises(NoActivePoll):
        # There is a round but there is no poll.
        backend.cast_vote(GAME_ID, ROUND_NAME, 'bob', GAME_CARDS[0])

    backend.add_poll(GAME_ID, ROUND_NAME)

    with pytest.raises(IllegalEstimation):
        # There is a poll but we've choosen a wrong card
        backend.cast_vote(GAME_ID, ROUND_NAME, 'bob', 'no such card')

    player_to_vote = dict(zip(PLAYERS, GAME_CARDS))

    for player, vote in player_to_vote.items():
        backend.cast_vote(GAME_ID, ROUND_NAME, player, vote)

    round = backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]
    assert round['finalized'] is False
    assert round['polls'] == [player_to_vote]

    # A player is able to change the vote:
    backend.cast_vote(GAME_ID, ROUND_NAME, PLAYERS[0], GAME_CARDS[3])
    player_to_vote[PLAYERS[0]] = GAME_CARDS[3]

    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == [player_to_vote]

    # Recasting the same vote should not change anything.
    for player, vote in player_to_vote.items():
        backend.cast_vote(GAME_ID, ROUND_NAME, player, vote)
    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == [player_to_vote]


def test_cast_vote_round_finalized(backend_with_a_poll):
    """Test if casting a vote to a finalized round results in an error."""
    backend = backend_with_a_poll
    backend.finalize_round(GAME_ID, ROUND_NAME)
    with pytest.raises(RoundFinalized):
        backend.cast_vote(GAME_ID, ROUND_NAME, 'player 1', GAME_CARDS[3])


def test_cast_vote_multiple_polls(backend_with_a_poll):
    """Test if the votes always go to the last poll."""
    backend = backend_with_a_poll
    player = 'JJ'
    vote = GAME_CARDS[3]

    backend.cast_vote(GAME_ID, ROUND_NAME, player, vote)
    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == [{player: vote}]

    backend.add_poll(GAME_ID, ROUND_NAME)
    second_vote = GAME_CARDS[5]
    backend.cast_vote(GAME_ID, ROUND_NAME, player, second_vote)

    assert backend.serialize_game(GAME_ID)['rounds'][ROUND_NAME]['polls'] == [
        {player: vote},
        {player: second_vote},
    ]
