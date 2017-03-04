import React, { Component } from 'react';
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
  maybeRenderPhoto() {
    let user = this.props.user;
    let metadata = user.metadata;
    if (metadata && metadata.company_profile_url) {
      return (
          <a href={metadata.company_profile_url}>
            <img alt="User Profile" className="profile-img" src={user.photo_url} />
          </a>
      );
    } else {
      return;
    }
  }
  department() {
    let metadata = this.props.metadata;
    if (metadata && metadata.department) {
      return <h4>{metadata.department}</h4>
    } else {
      return;
    }
  }
  business_title() {
    let metadata = this.props.metadata;
    if (metadata && metadata.business_title) {
      return <h4>{metadata.business_title}</h4>
    } else {
      return;
    }
  }
  render() {
    const { user } = this.props;
    return (
      <div>
        <div className="container-fluid">
          <div className="content">
            <div className="bio">
              <div className="about-me">
                <maybeRenderPhoto user={user} />
                <h2>{user.first_name} {user.last_name}</h2>
                <department metadata={user.metadata} />
                <business_title metadata={user.metadata} />
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
  getUser: React.PropTypes.func.isRequired,
  location: React.PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
  user: React.PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return { user: state.user };
}

export default connect(mapStateToProps, { getUser })(User);
