import { FETCH_PREFS } from '../actions/index';

const defaultValue = [
  {
    id: 'None',
    location: 'Unknown',
    title: 'No Meetings Set Up',
    timezone: 'America/Los_Angeles',
    size: 0,
    office: 'None',
    datetime: [],
  },
];

export default function (state = defaultValue, action) {
  switch (action.type) {
    case FETCH_PREFS:
      return action.payload.data;
    default:
      return state;
  }
}
