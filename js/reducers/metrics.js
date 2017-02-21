import { FETCH_METRICS } from '../actions/index';

export default function (state = [{ subscribed: 0, title: 'No Subscriptions', meetings: 0 }], action) {
  switch (action.type) {
    case FETCH_METRICS:
      return action.payload.data;
    default:
      return state;
  }
}
