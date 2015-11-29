import React from 'react';
import { Button } from 'react-bootstrap';

export default class Welcome extends React.Component {
  render() {
    return (
      <div>
        <h1 className="cover-heading">Play planning poker with your team.</h1>
        <p className="lead">Create a new session or join an existing one. No installation. No login required.</p>
        <p className="lead">
          <Button bsSize="large" href="#">Create game</Button>
          {' '}  {/* Breakable space, so that buttons are separated. */}
          <Button bsSize="large" href="#">Join game</Button>
        </p>
      </div>
    );
  }
}
