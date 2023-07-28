import axios from "axios";
import React, { Component } from "react";

class MeetingRequest extends Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.state = { key: "", email: "", loading: true };
  }

  componentDidMount() {
    axios.get("/email").then((res) => {
      axios
        .get(
          `/v1/meeting_request/${MeetingRequest.getMeetingSpecKey()}?email=${
            res.data.email
          }`,
        )
        .then((res2) => {
          this.setState({
            key: res2.data.key,
            email: res.data.email,
            loading: false,
          });
        });
    });
  }

  static getMeetingSpecKey() {
    const path = window.location.pathname.split("/");
    return path[path.length - 1];
  }

  handleSubmit() {
    const { key, email } = this.state;
    this.setState({ loading: true });
    axios
      .post("/v1/meeting_request/", {
        meeting_spec_key: MeetingRequest.getMeetingSpecKey(),
        meeting_request_key: key,
        email,
      })
      .then((res) => {
        this.setState({ key: res.data.key, email, loading: false });
      });
  }

  renderButton() {
    const { key, loading } = this.state;

    let btnMsg = "Ask for a Meeting this week.";
    let btnColor = "btn-success";
    if (key !== "") {
      btnMsg = "Remove request for a Meeting this week.";
      btnColor = "btn-danger";
    }

    return (
      <button
        type="button"
        onClick={this.handleSubmit}
        className={`btn ${btnColor} btn-lg left30`}
        disabled={loading}
      >
        {loading && (
          <>
            <span
              className="spinner-border spinner-border-sm mr-2"
              role="status"
              aria-hidden="true"
            />
            <span className="sr-only">Loading...</span>
          </>
        )}
        {btnMsg}
      </button>
    );
  }

  render() {
    return <div>{this.renderButton()}</div>;
  }
}

export default MeetingRequest;
