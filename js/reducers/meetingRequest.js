import { GET_REQ } from '../actions/index';


export default function (state = { key: '' }, action) {
  switch (action.type) {
    case GET_REQ:
      return action.payload.data;
    default:
      return state;
  }
}
