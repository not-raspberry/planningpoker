"""Testing adding a poll to a round."""


def test_add_poll(game_id, game_round, moderator):
    """Test if moderator can add a poll."""
    new_poll = moderator.post('/game/%s/round/%s/new_poll' % (game_id, game_round))
    assert new_poll.status_code == 200
    round_dict = new_poll.json()['game']['rounds'][game_round]

    assert round_dict['polls'] == [{}], 'An empty poll should be added.'


def test_add_poll_permissions(game_id, game_round, client):
    """Ensure non-moderators cannot request a new poll."""
    new_poll_forbidden = client.post('/game/%s/round/%s/new_poll' % (game_id, game_round))
    assert new_poll_forbidden.status_code == 403


def test_add_poll_errors(game_id, game_round, moderator):
    """Test validation of new poll requests."""
    new_poll_wrong_round = moderator.post('/game/%s/round/nosuchround/new_poll' % game_id)
    assert new_poll_wrong_round.status_code == 404
