"""Test casting votes by players and other crazy stuff."""


def test_cast_vote(game_id, game_round, game_poll, game_cards,
                   player, player_name, moderator, moderator_name):
    """Test players casting a vote."""
    player_vote = game_cards[0]
    cast_vote = player.post('/game/%s/round/%s/vote' % (game_id, game_round),
                            json={'vote': player_vote})
    assert cast_vote.status_code == 200
    poll_vote = cast_vote.json()['game']['rounds'][game_round]['polls'][0]
    assert poll_vote == {player_name: player_vote}

    # The moderator can vote too.
    moderator_vote = game_cards[2]
    moderator_cast_vote = moderator.post('/game/%s/round/%s/vote' % (game_id, game_round),
                                         json={'vote': moderator_vote})

    poll_votes = moderator_cast_vote.json()['game']['rounds'][game_round]['polls'][0]
    assert poll_votes == {player_name: player_vote, moderator_name: moderator_vote}


def test_cast_vote_validation(game_id, game_round, game_poll, game_cards, player, player_name):
    """Feed the Cast vote resource with invelid requests."""
    no_vote = player.post('/game/%s/round/%s/vote' % (game_id, game_round))
    assert no_vote.status_code == 400

    vote = game_cards[0]
    invalid_game_id = player.post('/game/123-NO-SUCH-GAME/round/%s/vote' % game_round,
                                  json={'vote': vote})
    assert invalid_game_id.status_code == 404

    no_such_round = player.post('/game/%s/round/AAA-INVALID-ROUND/vote' % game_round,
                                json={'vote': vote})
    assert no_such_round.status_code == 404

    invalid_vote = 123123
    assert invalid_vote not in game_cards
    invalid_vote = player.post('/game/%s/round/%s/vote' % (game_id, game_round),
                               json={'vote': invalid_vote})
    assert invalid_vote.status_code == 400


def test_cast_vote_round_finalized(game_id, game_round, game_poll, game_cards, player, moderator):
    """Check if cannot vote in finalized polls."""
    finalize_round = moderator.post('/game/%s/round/%s/finalize' % (game_id, game_round))
    assert finalize_round.ok

    cast_vote_finalized_poll = player.post('/game/%s/round/%s/vote' % (game_id, game_round),
                                           json={'vote': game_cards[1]})
    assert cast_vote_finalized_poll.status_code == 409


def test_cast_vote_permissions(game_id, game_round, game_poll, game_cards, client):
    """Check if a player that did not register cannot vote."""
    unregistered_vote = client.post('/game/%s/round/%s/vote' % (game_id, game_round),
                                    json={'vote': game_cards[2]})
    assert unregistered_vote.status_code == 401
