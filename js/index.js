import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import ReduxPromise from 'redux-promise';
import { Router, browserHistory } from 'react-router';

import reducers from './reducers';
import routes from './routes';

const store = applyMiddleware(ReduxPromise)(createStore);

ReactDOM.render(
  <Provider store={store(reducers)}>
    <Router history={browserHistory} routes={routes} />
  </Provider>,
  document.querySelector('#container'),
);
