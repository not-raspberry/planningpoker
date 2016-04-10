import React from 'react';
import { Button } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';


export default class Welcome extends React.Component {
    render() {
        return (
        <div>
            <h1 className="cover-heading">Play planning poker with your team.</h1>
            <p className="lead">Create a new session or join an existing one. No installation. No login required.</p>
            <p className="lead">
                <LinkContainer to="/create">
                    <Button bsSize="large">Create game</Button>
                </LinkContainer>
                {' '}  {/* Breakable space, so that buttons are separated. */}
                <Button bsSize="large" href="#">Join game</Button>
            </p>
        </div>
        );
    }
}
