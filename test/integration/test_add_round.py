"""Testing adding a round to a game."""


def test_add_round(game_id, moderator):
    """Test if a moderator can add a round to an owned game."""
    round_name = 'A round'

    new_round_no_name = moderator.post('/game/%s/new_round' % game_id)
    assert new_round_no_name.status_code == 400

    new_round_empty_name = moderator.post('/game/%s/new_round' % game_id, data={'round_name': ''})
    assert new_round_empty_name.status_code == 400

    new_round = moderator.post('/game/%s/new_round' % game_id, data={'round_name': round_name})
    assert new_round.status_code == 200
    game = new_round.json()['game']  # Response with full game state.
    assert game['rounds_order'] == [round_name]
    assert game['rounds'][round_name]['finalized'] is False, \
        'Newly created round should not be finalized.'


def test_add_round_permissions(game_id, client):
    """Test if a player cannot add a round to a game."""
    new_round = client.post('/game/%s/new_round' % game_id, data={'round_name': 'some round'})
    assert new_round.status_code == 403

    new_round_in_a_completely_made_up_game = client.post('/game/12312/new_round',
                                                         data={'round_name': 'some round'})
    assert new_round_in_a_completely_made_up_game.status_code == 403
