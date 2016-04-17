import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, hashHistory } from 'react-router'

import './ie10-viewport-bug-workaround.js';

import App from './components/app';
import Welcome from './components/welcome';
import CreateNewGame from './components/createNewGame';
import Game from './components/game';


ReactDOM.render(
    <Router history={hashHistory}>
        <Route path="/" component={App}>
            <IndexRoute component={Welcome} />
            <Route path="create" component={CreateNewGame} />
            <Route path="/game/:gameId" component={Game} />
        </Route>
    </Router>,
    document.getElementById('app'));
