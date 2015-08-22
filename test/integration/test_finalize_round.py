"""Test round finalization."""


def test_finalize_empty_round(game_id, game_round, moderator):
    """Test if the moderator cannot finalize an empty round."""
    finalize_empty = moderator.post('/game/%s/round/%s/finalize' % (game_id, game_round))
    assert finalize_empty.status_code == 404


def test_finalize_round(game_id, game_round, game_poll, moderator):
    """Test if the moderator can finalize a non-empty round."""
    finalize_round = moderator.post('/game/%s/round/%s/finalize' % (game_id, game_round))
    assert finalize_round.status_code == 200
    assert finalize_round.json()['game']['rounds'][game_round]['finalized'] is True

    finalize_round_again = moderator.post('/game/%s/round/%s/finalize' % (game_id, game_round))
    assert finalize_round_again.status_code == 409


def test_finalize_round_permission(game_id, game_round, game_poll, client):
    """Check if non-moderators cannot finalize a round."""
    client_finalize_round = client.post('/game/%s/round/%s/finalize' % (game_id, game_round))
    assert client_finalize_round.status_code == 403
