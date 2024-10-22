import axios from "axios";
import React from "react";

import { formatTimeSlot } from "../lib/datetime";

const formatTimeSlots = (timeSlots) => {
  const slotStrings = timeSlots.map(formatTimeSlot);
  return slotStrings.join(", ");
};

const formatRules = (rules, ruleLogic) => {
  if (rules.length === 1) {
    return `${rules[0].field}=="${rules[0].value}"`;
  }
  if (rules.length > 1) {
    return `${ruleLogic} of the ${rules.length} rules`;
  }
  return "No Rules";
};

function SubscriptionList() {
  const [subscriptions, setSubscriptions] = React.useState([]);
  React.useEffect(() => {
    axios.get("/v1/subscriptions").then((res) => {
      setSubscriptions(res.data);
    });
  }, []);
  return (
    <div className="container-fluid">
      <h1>Subscriptions</h1>
      <a className="btn btn-primary my-2" href="/admin/subscriptions/create">
        New Subscription
      </a>
      <table className="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>Office</th>
            <th>Size</th>
            <th>Default Auto Opt-In</th>
            <th>Rules</th>
            <th>Time Zone</th>
            <th>Time Slots</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((sub) => (
            <tr>
              <td>{sub.id}</td>
              <td>{sub.name}</td>
              <td>{sub.location}</td>
              <td>{sub.office}</td>
              <td>{sub.size}</td>
              <td>{sub.default_auto_opt_in.toString()}</td>
              <td>{formatRules(sub.rules, sub.rule_logic)}</td>
              <td>{sub.timezone}</td>
              <td>{formatTimeSlots(sub.time_slots)}</td>
              <td>
                <a href={`/admin/subscriptions/${sub.id}`}>edit</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SubscriptionList;
