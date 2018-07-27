import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import moment from 'moment-timezone';
import { postPreference } from '../actions/index';


class UserPreferenceForm extends Component {
  static isoDateToString(ISODate, timezone) {
    return moment(ISODate).tz(timezone).format('dddd LT z');
  }

  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.renderPreferences = this.renderPreferences.bind(this);
    this.renderTimes = this.renderTimes.bind(this);

    if (this.props.preferences.length !== 0) {
      this.state = this.props.preferences.reduce((preference) => {
        const dates = preference.datetime.reduce(datetime => ({ [datetime.id]: datetime.active }));
        return { [preference.id]: dates };
      });
    }
  }

  handleSubmit(prefId, event) {
    event.preventDefault();
    if (this.state) {
      this.props.postPreference(this.state[prefId], prefId);
      alert('Preference Updated'); // eslint-disable-line
    }
  }

  handleChange(event) {
    const data = {
      [event.target.value]: {
        [event.target.id]: event.target.checked,
      },
    };
    this.setState(prevState => Object.assign({}, prevState, data));
  }

  renderPreferences(state) {
    if (this.props.preferences.length !== 0) {
      return this.props.preferences.map(preference => (
        <div key={preference.id}>
          <h3>
            {preference.title}
          </h3>
          <h6>
            {preference.office}
,
            {' '}
            {preference.location}
            {' '}
(
            {preference.size}
)
          </h6>
          <form onSubmit={event => this.handleSubmit(preference.id, event)}>
            { this.renderTimes(preference, state) }
            <button type="submit" className="btn btn-danger left30">
              Set Preferences!
            </button>
          </form>
        </div>
      ));
    }
    return (
      <div>
No Subscription Available.
      </div>
    );
  }

  renderTimes(preference, state) {
    if (preference) {
      return preference.datetime.map((datetime) => {
        let checked = datetime.active;
        if (state === null) {
            // eslint-disable-line
        } else if (`${preference.id}` in state) {
          checked = state[`${preference.id}`][`${datetime.active}`];
        }
        return (
          <label htmlFor={datetime.id} key={datetime.id}>
            <input
              id={datetime.id}
              defaultChecked={checked}
              onChange={this.handleChange}
              value={preference.id}
              type="checkbox"
            />
            {UserPreferenceForm.isoDateToString(datetime.date, preference.timezone)}
          </label>
        );
      });
    }
    return (
      <div>
No data.
      </div>
    );
  }

  render() {
    return (
      <div>
        { this.renderPreferences(this.state) }
      </div>
    );
  }
}

UserPreferenceForm.propTypes = {
  postPreference: PropTypes.func.isRequired,
  preferences: PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return {
    datetime: state.datetime,
    timezone: state.timezone,
  };
}

export default connect(mapStateToProps, { postPreference })(UserPreferenceForm);
