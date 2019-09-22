import { FETCH_USER } from '../actions/index';

const defaultValue = {
  photo_url: 'https://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_large_assets/3f74899c069c/assets/img/illustrations/mascots/darwin@2x.png',
  first_name: 'Darwin',
  last_name: 'Yelp',
  email: 'darwin@yelp.com',
  metadata: {
    department: 'Consumer',
    company_profile_url: 'https://www.yelp.com/user_details?userid=nkN_do3fJ9xekchVC-v68A',
  },
};

export default function (state = defaultValue, action) {
  switch (action.type) {
    case FETCH_USER:
      return action.payload.data;
    default:
      return state;
  }
}
