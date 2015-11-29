import React from 'react';
import ReactDOM from 'react-dom';
import { Button } from 'react-bootstrap';

import './ie10-viewport-bug-workaround.js';

import App from './components/app';


ReactDOM.render(<App />, document.getElementById('app'));
