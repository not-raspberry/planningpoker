"""Testing game scenarios using the API."""


def test_create_new_game_ok(client):
    """Check if the resource respond to get with current games count."""
    no_cards_params = client.post('/new_game')
    assert no_cards_params.status_code == 400

    cards_in_query = client.post('/new_game', query={'cards': [1, 2, 3, 5, '?']})
    assert cards_in_query.status_code == 400

    assert client.get('/status').json()['games_count'] == 0

    new_game = client.post('/new_game', data={'cards': [1, 2, 3, 5, '?']})
    json = new_game.json()
    assert json.keys() == {'game_id'}
    assert isinstance(json['game_id'], str) and len(json['game_id']) > 10

    assert client.get('/status').json()['games_count'] == 1
