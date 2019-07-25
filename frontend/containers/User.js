import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { getUser } from '../actions/index';
import UserPreferences from './UserPreferences';


class User extends Component {
  componentWillMount() {
    this.props.getUser(this.getEmail());
  }

  getEmail() {
    let email = '';
    const path = this.props.location.pathname.split('/');
    if (path.indexOf('user') !== -1) {
      email = path[path.indexOf('user') + 1];
    }
    return email;
  }

  render() {
    const { user } = this.props;
    return (
      <div>
        <div className="container-fluid">
          <div className="content">
            <div className="bio">
              <div className="about-me">
                <a href={user.metadata.company_profile_url}>
                  <img alt="User Profile" className="profile-img" src={user.photo_url} />
                </a>
                <h2>
                  {user.first_name}
                  {' '}
                  {user.last_name}
                </h2>
                <h4>
                  {user.metadata.department}
                </h4>
                <h4>
                  {user.metadata.business_title}
                </h4>
                <br />
              </div>
            </div>
          </div>
          <UserPreferences email={this.getEmail()} />
        </div>
      </div>
    );
  }
}

User.propTypes = {
  getUser: PropTypes.func.isRequired,
  location: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
  user: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return { user: state.user };
}

export default connect(mapStateToProps, { getUser })(User);
