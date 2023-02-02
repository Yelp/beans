import axios from 'axios';
import React, { Component } from 'react';

class MeetingRequest extends Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.state = { key: '', email: '' };
  }

  componentDidMount() {
    axios.get('/email').then((res) => {
      axios.get(
        `/v1/meeting_request/${MeetingRequest.getMeetingSpecKey()}?email=${res.data.email}`,
      ).then((res2) => {
        this.setState({ key: res2.data.key, email: res.data.email });
      });
    });
  }

  static getMeetingSpecKey() {
    const path = window.location.pathname.split('/');
    return path[path.length - 1];
  }

  handleSubmit() {
    const { key, email } = this.state;
    axios.post(
      '/v1/meeting_request/',
      {
        meeting_spec_key: MeetingRequest.getMeetingSpecKey(),
        meeting_request_key: key,
        email,
      },
    ).then((res) => {
      this.setState({ key: res.data.key, email });
    });
  }

  renderButton() {
    const { key } = this.state;
    if (key === '') {
      return (
        <button type="button" onClick={this.handleSubmit} className="btn btn-success btn-lg left30">
          Ask for a Meeting this week.
        </button>
      );
    }
    return (
      <button type="button" onClick={this.handleSubmit} className="btn btn-danger btn-lg left30">
        Remove request for a Meeting this week.
      </button>
    );
  }

  render() {
    return (
      <div>
        {this.renderButton()}
      </div>
    );
  }
}

export default MeetingRequest;
