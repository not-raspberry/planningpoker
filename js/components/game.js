import React from 'react';
import { Row } from 'react-bootstrap';


// Game stub.
const Game = React.createClass({
    render: function() {
        const game = this.props.games[this.props.routeParams.gameId];
        return (
        <Row>
            <p className="lead">Planning poker game</p>
            <ul>
                <li>Rounds: {game.rounds.length ? game.rounds.join(', ') : 0}</li>
                <li>Players: {game.players.length ? game.players.join(', ') : 0}</li>
            </ul>
        </Row>
        );
    }
});

export default Game;
