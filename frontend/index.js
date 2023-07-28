import React from 'react';
import { createRoot } from 'react-dom/client';
import {
  BrowserRouter as Router,
  Route,
  Routes,
} from 'react-router-dom';

import Header from './components/Header';
import Footer from './components/Footer';

import MetricsList from './containers/MetricsList';
import MeetingRequest from './containers/MeetingRequest';
import User from './containers/User';
import SubscriptionsList from './containers/SubscriptionsList';
import Subscription from './containers/Subscription';

const root = createRoot(document.querySelector('#container'));
root.render(
  <Router>
    <div>
      <Header />
      <Routes>
        <Route exact path="/" element={<User />} />
        <Route path="/dashboard" element={<MetricsList />} />
        <Route path="/user/:email" element={<User />} />
        <Route path="/meeting_request/:id" element={<MeetingRequest />} />
        <Route path="/admin/subscriptions/:id" element={<Subscription />} />
        <Route exact path="/admin/subscriptions" element={<SubscriptionsList />} />
      </Routes>
      <Footer />
    </div>
  </Router>,
);
