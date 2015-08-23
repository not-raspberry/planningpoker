"""Testing game scenarios using the API."""
import pytest


def test_create_new_game_no_cards_error(client):
    """Check if when the 'cards' POST parameter is missing, an error is returned."""
    no_post_data = client.post('/new_game')
    assert no_post_data.status_code == 400
    assert no_post_data.json()['error'] == 'No card set provided.'

    cards_param = {'cards': [1, 2, 3, 5, '?']}
    name_param = {'moderator_name': 'Francis'}

    both_request_params = {}
    both_request_params.update(cards_param)
    both_request_params.update(name_param)

    empty_cards_param = both_request_params.copy()
    empty_cards_param['cards'] = []

    # Params list in query string, not in POST data.
    params_in_query = client.post('/new_game', query=both_request_params)
    assert params_in_query.status_code == 400

    no_cards = client.post('/new_game', query=name_param)
    assert no_cards.status_code == 400

    no_moderator_name = client.post('/new_game', query=cards_param)
    assert no_moderator_name.status_code == 400

    empty_cards_list = client.post('/new_game', data=empty_cards_param)
    assert empty_cards_list.status_code == 400

    assert client.get('/status').json()['games_count'] == 0


@pytest.mark.parametrize('cards', [
    [1],
    ['?'],
    ['its_just_as_my_pm_says'],
])
def test_create_new_game_too_small_cards_set_error(client, cards):
    """Check if attempts to create a new game with less that 2 cards result in an error."""
    too_little_cards = client.post('/new_game', data={'cards': cards, 'moderator_name': 'Tim'})
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
    moderator_name = 'Alice'
    new_game = client.post('/new_game', data={'cards': cards, 'moderator_name': moderator_name})
    json = new_game.json()

    # Random game ID returned (no real way to test randomness):
    assert json.keys() == {'game_id', 'game'}
    assert isinstance(json['game_id'], str)
    assert len(json['game_id']) > 10

    # Empty game is returned.
    assert json['game'] == {
        'players': [moderator_name],
        'cards': cards,
        'rounds_order': [],
        'rounds': {},
    }

    assert client.get('/status').json()['games_count'] == 1


def test_create_2_games(client):
    """Check if after creating 2 games the user has moderator access to both of them."""
    game_1 = client.post('/new_game', data={'cards': [1, 3, 5], 'moderator_name': 'Robert'})
    game_2 = client.post('/new_game', data={'cards': [1, 3, 5, 10, '?'], 'moderator_name': 'Bobby'})

    game_1_id = game_1.json()['game_id']
    game_2_id = game_2.json()['game_id']

    new_round_game_1 = client.post('/game/%s/new_round' % game_1_id, data={'round_name': 'round'})
    assert new_round_game_1.status_code == 200
    new_round_game_2 = client.post('/game/%s/new_round' % game_2_id, data={'round_name': 'round'})
    assert new_round_game_2.status_code == 200
