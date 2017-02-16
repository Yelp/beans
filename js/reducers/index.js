import { combineReducers } from 'redux';
import metrics from './metrics';
import user from './user';
import preferences from './preferences';
import meetingRequest from './meetingRequest';

const rootReducer = combineReducers({
  metrics,
  preferences,
  user,
  meetingRequest,
});

export default rootReducer;
