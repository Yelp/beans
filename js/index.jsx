import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import ReduxPromise from 'redux-promise';
import {
  BrowserRouter as Router,
  Route,
} from 'react-router-dom';

import reducers from './reducers';
import Header from './components/Header';
import Footer from './components/Footer';

import MetricsList from './containers/MetricsList';
import MeetingRequest from './containers/MeetingRequest';
import User from './containers/User';

const store = applyMiddleware(ReduxPromise)(createStore)(reducers);

ReactDOM.render(
  <Provider store={store}>
    <Router>
      <div>
        <Header />
        <Route exact path="/" component={User} />
        <Route path="/dashboard" component={MetricsList} />
        <Route path="/user/:email" component={User} />
        <Route path="/meeting_request/:id" component={MeetingRequest} />
        <Footer />
      </div>
    </Router>
  </Provider>,
  document.querySelector('#container'),
);

