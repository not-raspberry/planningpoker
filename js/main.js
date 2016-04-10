import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute } from 'react-router'

import './ie10-viewport-bug-workaround.js';

import App from './components/app';
import Welcome from './components/welcome';
import CreateNewGame from './components/createNewGame';


ReactDOM.render(
    <Router>
        <Route path="/" component={App}>
            <IndexRoute component={Welcome} />
            <Route path="create" component={CreateNewGame} />
        </Route>
    </Router>,
    document.getElementById('app'));
