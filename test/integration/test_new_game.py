"""Testing game scenarios using the API."""
import pytest


def test_create_new_game_no_cards_error(client):
    """Check if when the 'cards' POST parameter is missing, an error is returned."""
    no_cards_param = client.post('/new_game')
    assert no_cards_param.status_code == 400
    assert no_cards_param.json()['error'] == 'No card set provided.'

    # Cards list in query string, not in POST data.
    cards_in_query = client.post('/new_game', query={'cards': [1, 2, 3, 5, '?']})
    assert cards_in_query.status_code == 400
    assert cards_in_query.json()['error'] == 'No card set provided.'

    empty_cards_list = client.post('/new_game', data={'cards': []})
    assert empty_cards_list.status_code == 400
    assert empty_cards_list.json()['error'] == 'No card set provided.'

    assert client.get('/status').json()['games_count'] == 0


@pytest.mark.parametrize('cards', [
    [1],
    ['?'],
    ['its_just_as_my_pm_says'],
])
def test_create_new_game_too_small_cards_set_error(client, cards):
    """Check if attempts to create a new game with less that 2 cards result in an error."""
    too_little_cards = client.post('/new_game', data={'cards': cards})
    assert too_little_cards.status_code == 400
    assert too_little_cards.json()['error'] == 'Cannot play with less than 2 cards.'

    assert client.get('/status').json()['games_count'] == 0


@pytest.mark.parametrize('cards', [
    [1, 2],
    list(range(20)),
    [2 ** n for n in range(20)],
    [1, 2, 3, 5, 9, 15, 23, 'dunno', 'break?'],
])
def test_create_new_game_ok(client, cards):
    """Test creation of a new game."""
    new_game = client.post('/new_game', data={'cards': cards})
    json = new_game.json()

    # Random game ID returned (no real way to test randomness):
    assert json.keys() == {'game_id', 'game'}
    assert isinstance(json['game_id'], str)
    assert len(json['game_id']) > 10

    # Empty game is returned.
    assert json['game'] == {
        'players': [],
        'cards': cards,
        'rounds_order': [],
        'rounds': {},
    }

    assert client.get('/status').json()['games_count'] == 1
