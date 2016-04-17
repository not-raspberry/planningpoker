"""Testing '/status' resource."""


def test_status_resource(client):
    """Check if the resource respond to get with current games count."""
    get_status = client.get('/status')
    assert get_status.status_code == 200
    assert get_status.json() == {'games_count': 0}

    client.post('/new_game', json={'cards': [1, 2, 3], 'moderator_name': 'Y.'})

    get_status_with_a_game = client.get('/status')
    assert get_status_with_a_game.status_code == 200
    assert get_status_with_a_game.json() == {'games_count': 1}
