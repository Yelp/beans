import axios from "axios";
import React from "react";
import PropTypes from "prop-types";

import { formatTimeSlot } from "../lib/datetime";

const getSubscriptionId = () => {
  const path = window.location.pathname.split("/");
  return path[path.length - 1];
};

const getAutoOptIn = () => {
  const searchParams = new URLSearchParams(window.location.search);
  const autoOptIn = searchParams.get("auto_opt_in");
  if (autoOptIn == null) {
    return null;
  }
  return ["1", "t", "true", "y", "yes"].contains(autoOptIn);
};

function SubscribedMessage({ subscription, timeSlot, newPreference }) {
  let msg = "have been";
  if (!newPreference) {
    msg = "were already";
  }
  return (
    <div>
      <h1>
        You {msg} subscribed to {subscription.name} for{" "}
        <span className="text-nowrap h1">{formatTimeSlot(timeSlot)}</span>
      </h1>
      <p>You will be redirected to the home page in 5 seconds...</p>
    </div>
  );
}

SubscribedMessage.propTypes = {
  subscription: PropTypes.shape({
    name: PropTypes.string.isRequired,
    timezone: PropTypes.string.isRequired,
  }).isRequired,
  timeSlot: PropTypes.shape({
    day: PropTypes.string.isRequired,
    hour: PropTypes.number.isRequired,
    minute: PropTypes.number.isRequired,
  }).isRequired,
  newPreference: PropTypes.bool.isRequired,
};

function ErrorMessage({ error }) {
  return <div>Error subscribing you. {error.msg}</div>;
}

ErrorMessage.propTypes = {
  error: PropTypes.shape({
    msg: PropTypes.string.isRequired,
  }).isRequired,
};

function Subscribe() {
  const [subscribedSubscription, setSubscribedSubscription] = React.useState();
  const [error, setError] = React.useState();

  const errorHandler = (err) => {
    if (err.response) {
      setError(err.response.data);
    } else {
      setError({ msg: "Unknown error on the backend" });
    }
  };

  React.useEffect(() => {
    axios
      .get("/email")
      .then((resEmail) => {
        axios
          .post(`/v1/user/preferences/subscribe/${getSubscriptionId()}`, {
            email: resEmail.data.email,
            auto_opt_in: getAutoOptIn(),
          })
          .then((resSubscribe) => {
            setSubscribedSubscription(resSubscribe.data);
            // In 5 seconds redirect to home page
            setTimeout(() => window.location.assign("/"), 5000);
          })
          .catch(errorHandler);
      })
      .catch(errorHandler);
  }, []);

  if (!error && !subscribedSubscription) {
    return (
      <div className="d-flex justify-content-center align-items-center">
        <div className="spinner-border mr-2" role="status" />
        <h1>Subscribing...</h1>
      </div>
    );
  }

  return (
    <div className="container mt-2 text-center">
      {error && <ErrorMessage error={error} />}
      {subscribedSubscription && (
        <SubscribedMessage
          subscription={subscribedSubscription.subscription}
          timeSlot={subscribedSubscription.time_slot}
          newPreference={subscribedSubscription.new_preference}
        />
      )}
    </div>
  );
}

export default Subscribe;
