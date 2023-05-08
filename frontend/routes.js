import React from 'react';
import { Route, IndexRoute } from 'react-router';

import MetricsList from './containers/MetricsList';
import MeetingRequest from './containers/MeetingRequest';
import User from './containers/User';
import SubscriptionsList from './containers/SubscriptionsList';
import Subscription from './containers/Subscription';
import App from './App';

export default (
  <Route path="/" component={App}>
    <IndexRoute component={User} />
    <Route path="/dashboard" component={MetricsList} />
    <Route path="/user/:email" component={User} />
    <Route path="/meeting_request/:id" component={MeetingRequest} />
    <Route path="/admin/subscriptions/:id" component={Subscription} />
    <Route path="/admin/subscriptions" component={SubscriptionsList} />
  </Route>
);
