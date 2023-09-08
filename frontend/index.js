import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Header from "./components/Header";
import Footer from "./components/Footer";

import MetricsList from "./containers/MetricsList";
import MeetingRequest from "./containers/MeetingRequest";
import User from "./containers/User";
import SubscriptionsList from "./containers/SubscriptionsList";
import Subscription from "./containers/Subscription";

const router = createBrowserRouter([
  {
    path: "/",
    element: <User />,
  },
  {
    path: "/dashboard",
    element: <MetricsList />,
  },
  {
    path: "/user/:email",
    element: <User />,
  },
  {
    path: "/meeting_request/:id",
    element: <MeetingRequest />,
  },
  {
    path: "/admin/subscriptions/:id",
    element: <Subscription />,
  },
  {
    path: "/admin/subscriptions",
    element: <SubscriptionsList />,
  },
]);

const root = createRoot(document.querySelector("#container"));
root.render(
  <div>
    <Header />
    <RouterProvider router={router} />
    <Footer />
  </div>,
);
