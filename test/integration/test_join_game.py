"""Test joining game as a player."""


def test_join_game(game_id, client, another_client, moderator_name):
    """Test if clients can join a game."""
    name = 'Bob'
    join_game = client.post('/game/%s/join' % game_id, data={'name': name})
    assert join_game.status_code == 200
    assert sorted(join_game.json()['game']['players']) == sorted([name, moderator_name])

    join_game_again = client.post('/game/%s/join' % game_id, data={'name': name})
    assert join_game_again.status_code == 409
    assert (join_game_again.json()['error'] ==
            'The client is already registered in this game.')

    # Another player tries to join the game with the same name:
    join_game_name_already_taken = another_client.post('/game/%s/join' % game_id,
                                                       data={'name': name})
    assert join_game_name_already_taken.status_code == 409
    assert (join_game_name_already_taken.json()['error'] ==
            'There is already a player with such name in the game.')

    # Another player tries to join the game with another name:
    another_name = 'Rob'
    join_game_another_session = another_client.post('/game/%s/join' % game_id,
                                                    data={'name': another_name})
    assert join_game_another_session.status_code == 200
    players = join_game_another_session.json()['game']['players']
    assert sorted(players) == sorted([name, moderator_name, another_name])


def test_join_game_error(game_id, client):
    """Test the Join game resource with invalid input."""
    join_game_no_name = client.post('/game/%s/join' % game_id)
    assert join_game_no_name.status_code == 400

    join_game_empty_name = client.post('/game/%s/join' % game_id, data={'name': ''})
    assert join_game_empty_name.status_code == 400

    join_nonexistent_game = client.post('/game/123123/join', data={'name': 'Me'})
    assert join_nonexistent_game.status_code == 404
