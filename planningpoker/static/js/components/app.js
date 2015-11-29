import React from 'react';
import { Router, Route, Link } from 'react-router'

import Welcome from './welcome';


export default class App extends React.Component {
  render() {
    return (
        <Router>
            <Route path="/" component={Welcome} />
        </Router>
    );
  }
}
