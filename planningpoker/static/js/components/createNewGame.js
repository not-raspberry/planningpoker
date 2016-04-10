import React from 'react';
import { Button } from 'react-bootstrap';


export default class CreateNewGame extends React.Component {
  render() {
    return (
    <div>
        <p className="lead">Create a new game.</p>
        <p className="lead">
            <Button bsSize="large" href="#">Create game</Button>
        </p>
    </div>
    );
  }
}
