import axios from 'axios';

export const FETCH_METRICS = 'FETCH_METRICS';
export const FETCH_PREFS = 'FETCH_PREFS';
export const POST_PREFS = 'POST_PREFS';
export const GET_REQ = 'GET_REQ';
export const FETCH_USER = 'FETCH_USER';
export const FETCH_EMAIL = 'FETCH_EMAIL';

function apiGetRequest(url, type) {
  const request = axios.get(url);
  return {
    type,
    payload: request,
  };
}

function apiPostRequest(url, props, type) {
  const request = axios.post(url, props);
  return {
    type,
    payload: request,
  };
}

export function getMetrics(version) {
  return apiGetRequest(`/${version}/metrics/`, FETCH_METRICS);
}

export function getPreferences(email) {
  if (email === '') {
    return ((dispatch) => {
      axios.get('/email').then((res) => {
        dispatch(apiGetRequest(`/v1/user/preferences/?email=${res.data.email}`, FETCH_PREFS));
      });
    });
  }
  return apiGetRequest(`/v1/user/preferences/?email=${email}`, FETCH_PREFS);
}

export function getUser(email) {
  if (email === '') {
    return ((dispatch) => {
      axios.get('/email').then((res) => {
        dispatch(apiGetRequest(`/v1/user/?email=${res.data.email}`, FETCH_USER));
      });
    });
  }
  return apiGetRequest(`/v1/user/?email=${email}`, FETCH_USER);
}

export function postPreference(state, id) {
  return ((dispatch) => {
    axios.get('/email').then((res) => {
      dispatch(apiPostRequest(`/v1/user/preferences/subscription/${id}`, { ...state, email: res.data.email }, POST_PREFS));
    });
  });
}

export function getMeetingRequest(id) {
  return ((dispatch) => {
    axios.get('/email').then((res) => {
      dispatch(apiGetRequest(`/v1/meeting_request/${id}?email=${res.data.email}`, GET_REQ));
    });
  });
}
