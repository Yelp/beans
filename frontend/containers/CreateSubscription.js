import axios from "axios";
import React from "react";

import { prepareSubscriptionPayload } from "../lib/subscription";
import EditSubscription from "../components/EditSubscription";
import DisplayErrorMessage from "../components/DisplayErrors";

const DEFAULT_OPTIONS = {
  location: "Online",
  name: "",
  office: "Remote",
  rule_logic: null,
  rules: [],
  size: 2,
  time_slots: [],
  timezone: "America/Los_Angeles",
  default_auto_opt_in: false,
};

function CreateSubscription() {
  const [subscription, setSubscription] = React.useState({
    ...DEFAULT_OPTIONS,
  });
  const [saving, setSaving] = React.useState(false);
  const [errors, setErrors] = React.useState(null);

  const createSubscription = () => {
    setSaving(true);
    const payloadSubscription = prepareSubscriptionPayload(subscription);

    setSaving(false);
    axios
      .post(`/v1/subscriptions/`, payloadSubscription)
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
          setErrors([{ msg: "Error sending POST request to server" }]);
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
        onClick={createSubscription}
        disabled={saving}
      >
        Create
      </button>
    </div>
  );
}

export default CreateSubscription;
