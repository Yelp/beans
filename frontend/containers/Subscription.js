import axios from "axios";
import React from "react";

import { addUUID, prepareSubscriptionPayload } from "../lib/subscription";
import EditSubscription from "../components/EditSubscription";
import DisplayErrorMessage from "../components/DisplayErrors";

const getSubscriptionId = () => {
  const path = window.location.pathname.split("/");
  return path[path.length - 1];
};

function Subscription() {
  const [subscription, setSubscription] = React.useState(null);
  const [saving, setSaving] = React.useState(false);
  const [errors, setErrors] = React.useState(null);

  React.useEffect(() => {
    axios.get(`/v1/subscriptions/${getSubscriptionId()}`).then((res) => {
      const newSubscription = { ...res.data };
      newSubscription.rules = addUUID(newSubscription.rules);
      newSubscription.time_slots = addUUID(newSubscription.time_slots);
      setSubscription(newSubscription);
    });
  }, []);

  if (subscription == null) {
    return "";
  }

  const updateSubscription = () => {
    setSaving(true);
    const { id, ...subscriptionData } = subscription;
    const payloadSubscription = prepareSubscriptionPayload(subscriptionData);
    setSaving(false);
    axios
      .put(`/v1/subscriptions/${id}`, payloadSubscription)
      .then(() => {
        setSaving(false);
        setErrors(null);
        window.location.assign("/admin/subscriptions");
      })
      .catch((error) => {
        setSaving(false);
        if (error.response) {
          setErrors(error.response.data);
        } else {
          setErrors([{ msg: "Error sending PUT request to server" }]);
        }
      });
  };

  return (
    <div className="container mt-2">
      {errors && <DisplayErrorMessage errors={errors} />}
      <EditSubscription
        subscription={subscription}
        setSubscription={setSubscription}
      />
      <button
        type="button"
        className="btn btn-primary mt-2"
        onClick={updateSubscription}
        disabled={saving}
      >
        Update
      </button>
    </div>
  );
}

export default Subscription;
