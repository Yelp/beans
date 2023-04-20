import axios from 'axios';
import React, { Component } from 'react';
import PropTypes from 'prop-types';

import moment from 'moment-timezone';

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
    const { preferences } = this.props;

    if (preferences.length !== 0) {
      this.state = preferences.reduce((preference) => {
        const dates = preference.datetime.reduce(
          (datetime) => ({ [datetime.id]: datetime.active }),
        );
        return { [preference.id]: dates };
      });
    }
  }

  handleSubmit(prefId, event) {
    event.preventDefault();
    if (this.state) {
      axios.post(
        `/v1/user/preferences/subscription/${prefId}`,
        { ...this.state[prefId], email: this.props.email },
      ).then(() => {
        alert('Preference Updated'); // eslint-disable-line
      });
    }
  }

  handleChange(event) {
    const data = {
      [event.target.value]: {
        [event.target.id]: event.target.checked,
      },
    };
    this.setState((prevState) => ({ ...prevState, ...data }));
  }

  renderPreferences(state) {
    const { preferences } = this.props;
    if (preferences.length !== 0) {
      return preferences.map((preference) => (
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
          <div>
            { this.renderTimes(preference, state) }
            <button type="button" onClick={(event) => this.handleSubmit(preference.id, event)} className="btn btn-danger left30">
              Set Preferences!
            </button>
          </div>
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
  email: PropTypes.string.isRequired,
  preferences: PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default UserPreferenceForm;
