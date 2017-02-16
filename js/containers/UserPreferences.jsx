import React, { Component } from 'react';
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
  getPreferences: React.PropTypes.func.isRequired,
  email: React.PropTypes.string.isRequired, // eslint-disable-line react/forbid-prop-types
  preferences: React.PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return { preferences: state.preferences };
}

export default connect(mapStateToProps, { getPreferences })(UserPreferences);
