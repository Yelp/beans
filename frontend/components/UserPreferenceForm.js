import axios from "axios";
import React, { Component } from "react";
import PropTypes from "prop-types";
import Switch from "react-switch";
import moment from "moment-timezone";
import { Tooltip } from "react-tooltip";

class UserPreferenceForm extends Component {
  static isoDateToString(ISODate, timezone) {
    return moment(ISODate).tz(timezone).format("dddd LT z");
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
        const dates = preference.datetime.reduce((datetime) => ({
          [datetime.id]: datetime.active,
        }));
        return { [preference.id]: dates };
      });
    }
  }

  handleSubmit(prefId, event) {
    event.preventDefault();
    if (this.state) {
      axios
        .post(`/v1/user/preferences/subscription/${prefId}`, {
          ...this.state[prefId],
          email: this.props.email,
        })
        .then(() => {
          alert("Preference Updated"); // eslint-disable-line
        });
    }
  }

  handleChange(value, id, field, defaults = {}) {
    const [prefId, dateId] = id.split("-");
    this.setState((prevState) => {
      const { [prefId]: dataForPreference = {} } = prevState;
      const { [dateId]: dataForDate = {} } = dataForPreference;

      dataForDate[field] = value;
      Object.keys(defaults).forEach((key) => {
        if (dataForDate[key] === undefined) {
          dataForDate[key] = defaults[key];
        }
      });

      dataForPreference[dateId] = dataForDate;
      return { ...prevState, ...{ [prefId]: dataForPreference } };
    });
  }

  renderPreferences(state) {
    const { preferences } = this.props;
    if (preferences.length !== 0) {
      return preferences.map((preference) => (
        <div key={`${preference.id}-${preference.title}`}>
          <div className="preference-header">
            <h3>{preference.title}</h3>
            <h6>
              {preference.office}, {preference.location} ({preference.size})
            </h6>
          </div>
          <div className="preference-options">
            {this.renderTimes(preference, state)}
            <button
              type="button"
              onClick={(event) => this.handleSubmit(preference.id, event)}
              className="btn btn-danger"
            >
              Set Preferences!
            </button>
          </div>
        </div>
      ));
    }
    return <div className="no-subscriptions">No Subscription Available.</div>;
  }

  renderTimes(preference, state) {
    if (preference) {
      return preference.datetime.map((datetime) => {
        let {
          active,
          auto_opt_in: autoOptIn = preference.default_auto_opt_in,
        } = datetime;
        if (state === null) {
          // eslint-disable-line
        } else if (state[preference.id]?.[datetime.id] !== undefined) {
          active = state[preference.id]?.[datetime.id].active;
          autoOptIn =
            state[preference.id]?.[datetime.id].auto_opt_in ??
            preference.default_auto_opt_in;
        }
        const id = `${preference.id}-${datetime.id}`;
        return (
          <fieldset>
            <legend>
              {UserPreferenceForm.isoDateToString(
                datetime.date,
                preference.timezone,
              )}
            </legend>

            {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
            <label htmlFor={`${id}-subscribe`} key={`${id}-subscribe-label`}>
              Subscribe
              <Switch
                id={`${id}-subscribe`}
                key={`${id}-subscribe`}
                checked={active}
                onChange={(checked) =>
                  this.handleChange(checked, id, "active", {
                    auto_opt_in: autoOptIn,
                  })
                }
              />
            </label>

            {active && (
              <>
                {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                <label
                  htmlFor={`${id}-autoOptIn`}
                  key={`${id}-autoOptIn-label`}
                  className="autoOptIn"
                >
                  Auto opt-in to weekly matches
                  <Switch
                    id={`${id}-autoOptIn`}
                    key={`${id}-autoOptIn`}
                    checked={autoOptIn}
                    onChange={(checked) =>
                      this.handleChange(checked, id, "auto_opt_in", { active })
                    }
                  />
                </label>
                <Tooltip
                  content="When enabled, you will be automatically opted in for weekly matches. If disabled, you will need to manually opt-in for matches each week through the email sent from beans@yelp.com."
                  style={{
                    maxWidth: "350px",
                    borderRadius: "7px",
                    textAlign: "left",
                    fontSize: "12px",
                  }}
                  anchorSelect=".autoOptIn"
                  place="bottom-start"
                />
              </>
            )}
          </fieldset>
        );
      });
    }
    return <div>No data.</div>;
  }

  render() {
    if (this.props.loading) {
      return (
        <div className="spinner-border preferences-spinner" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      );
    }
    return <div>{this.renderPreferences(this.state)}</div>;
  }
}

UserPreferenceForm.propTypes = {
  email: PropTypes.string.isRequired,
  preferences: PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
  loading: PropTypes.bool.isRequired,
};

export default UserPreferenceForm;
