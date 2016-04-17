import React from 'react';
import { ButtonInput, Input, Alert, Row, Col } from 'react-bootstrap';
import xhr from 'xhr';


const CreateNewGame = React.createClass({
    getInitialState: function() {
        return {
            moderatorName: '',
            cards: '0, 1, 2, 3, 5, 8, 13, 20, 40, OMG',
            error: null,
        };
    },

    handleSubmit: function(event) {
        const moderatorName = this.state.moderatorName.trim();
        const cards = this.state.cards.split(',').map(s => s.trim());
        this.setState({error: null});

        let gameResp = xhr({
            method: 'post',
            url: '/new_game',
            json: {cards: cards, moderator_name: moderatorName}
        }, (err, resp) => {
            console.log(err, resp);
            if (err) {
                this.setState({error: {type: 'Connection error', message: 'Check your connection.'}});
                console.error('Network error:', err);
            } else if (resp.statusCode >= 400 && resp.statusCode <= 500) {
                this.setState({error: {type: 'Validation error', message: resp.body.error}});
                console.error('Response:', resp);
            } else {
                this.props.gameCreated(resp.body);
            }
        });
    },

    render: function(event) {
        const error = this.state.error && (
            <Row>
                <Col md={8} mdOffset={2}>
                    <Alert bsStyle="danger">
                        <strong>{this.state.error.type}:</strong> {this.state.error.message}
                    </Alert>
                </Col>
            </Row>
        );

        return (
        <form className="form-horizontal" onSubmit={this.handleSubmit}>
            <p className="lead">Create a new game</p>

            {error}


            <Input type="text"
                value={this.state.name}
                placeholder="Moderator name"
                label="Your name:"
                labelClassName="col-md-2" wrapperClassName="col-md-8"
                onChange={e => this.setState({'moderatorName': e.target.value})}
            />
            <Input type="text"
                value={this.state.cards}
                help="Comma-separated list of the cards in the game"
                label="Cards:"
                labelClassName="col-md-2" wrapperClassName="col-md-8"
                onChange={e => this.setState({'cards': e.target.value})}
            />

            <span className="lead">
                <ButtonInput type="submit"
                    value="Create game"
                    bsStyle={this.state.style} bsSize="large"
                    disabled={this.state.disabled}
                />
            </span>
        </form>
        );
    }
});

export default CreateNewGame;
