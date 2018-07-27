import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { getPreferences } from '../actions/index';
import UserPreferenceForm from '../components/UserPreferenceForm';


class UserPreferences extends Component {
  componentWillMount() {
    this.props.getPreferences(this.props.email);
  }

  render() {
    return (
      <div className="preferences">
        <UserPreferenceForm preferences={this.props.preferences} />
      </div>
    );
  }
}

UserPreferences.propTypes = {
  getPreferences: PropTypes.func.isRequired,
  email: PropTypes.string.isRequired, // eslint-disable-line react/forbid-prop-types
  preferences: PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return { preferences: state.preferences };
}

export default connect(mapStateToProps, { getPreferences })(UserPreferences);
