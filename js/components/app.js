import React from 'react';


// Wrapper for routes and crude state store.
const App = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
    },

    getInitialState: function() {
        return {
            // Game ID to game state maps.
            games: {},
            moderatedGamesIds: [],
        };
    },

    gameCreated: function(jsonResponse) {
        const {game_id: gameId, game: gameState} = jsonResponse;
        this.setState({
            games: {[gameId]: gameState, ...this.state.games},
            moderatedGamesIds: [gameId, ...this.state.moderatedGamesIds],
        });
        this.context.router.push('/game/' + gameId)
        console.log('Game', gameId, 'created:', gameState);

    },

    // Pass 'action' callbacks and store the the children.
    render: function() {
        return React.cloneElement(
            this.props.children,
            {
                gameCreated: this.gameCreated,
                ...this.state
            }
        );
    }
});

export default App;
