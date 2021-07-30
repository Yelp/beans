import axios from 'axios';
import React, { Component } from 'react';

import UserPreferences from './UserPreferences';

class User extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: {
        photo_url: 'https://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_large_assets/3f74899c069c/assets/img/illustrations/mascots/darwin@2x.png',
        first_name: 'Darwin',
        last_name: 'Yelp',
        email: 'darwin@yelp.com',
        metadata: {
          department: 'Consumer',
          company_profile_url: 'https://www.yelp.com/user_details?userid=nkN_do3fJ9xekchVC-v68A',
        },
      },
    };
  }

  componentDidMount() {
    axios.get('/email').then((res) => {
      axios.get(`/v1/user/?email=${res.data.email}`).then((res2) => {
        this.setState({ user: res2.data });
      });
    });
  }

  render() {
    const { user } = this.state;
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
          <UserPreferences />
        </div>
      </div>
    );
  }
}

export default User;
