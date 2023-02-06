import axios from 'axios';
import React from 'react';
import PropTypes from 'prop-types';

const DAYS_OF_THE_WEEK = [
  { label: 'Sunday', value: 'sunday' },
  { label: 'Monday', value: 'monday' },
  { label: 'Tuesday', value: 'tuesday' },
  { label: 'Wednesday', value: 'wednesday' },
  { label: 'Thursday', value: 'thursday' },
  { label: 'Friday', value: 'friday' },
  { label: 'Saturday', value: 'saturday' },
];

const RULE_LOGIC_OPTIONS = [
  { label: 'All', value: 'all' },
  { label: 'Any', value: 'any' },
];

const RuleShape = PropTypes.shape({
  field: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
});
const TimeSlotShape = PropTypes.shape({
  day: PropTypes.string.isRequired,
  hour: PropTypes.number.isRequired,
  minute: PropTypes.number.isRequired,
});

const getSubscriptionId = () => {
  const path = window.location.pathname.split('/');
  return path[path.length - 1];
};

const StringField = ({
  field, label, value, inputClassName,
}) => (
  <div className="form-group">
    <label htmlFor={field}>
      {label}
    </label>
    <input type="text" className={`form-control ${inputClassName}`} id={field} value={value} required />
  </div>
);

StringField.propTypes = {
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  inputClassName: PropTypes.string,
};

StringField.defaultProps = {
  inputClassName: '',
};

const NumberField = ({ field, label, value }) => (
  <div className="form-group">
    <label htmlFor={field}>
      {label}
    </label>
    <input type="number" className="form-control" id={field} value={value} required />
  </div>
);

NumberField.propTypes = {
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
};

const RuleField = ({ rule, index }) => {
  const ruleFieldId = `rule-${index}-field`;
  const ruleValueId = `rule-${index}-value`;
  // I can't figure out how to make this pass and they do have an related control
  /* eslint-disable jsx-a11y/label-has-associated-control */
  return (
    <div className="form-row mt-2">
      <label htmlFor={ruleFieldId} className="col-form-label">
        Field:
      </label>
      <div className="col">
        <input type="text" className="form-control" id={ruleFieldId} value={rule.field} required />
      </div>
      <label htmlFor={ruleValueId} className="col-form-label">
        Value:
      </label>
      <div className="col">
        <input type="text" className="form-control" id={ruleValueId} value={rule.value} required />
      </div>
      <div className="col-auto">
        <button type="button" className="btn btn-outline-danger btn-sm mt-1">Remove</button>
      </div>
    </div>
  );
  /* eslint-enable jsx-a11y/label-has-associated-control */
};

RuleField.propTypes = {
  rule: RuleShape.isRequired,
  index: PropTypes.number.isRequired,
};

// I can't figure out how to make this pass and they do have an related control
/* eslint-disable jsx-a11y/label-has-associated-control */
const RulesField = ({ rules, ruleLogic }) => (
  <div className="form-group">
    <h3>Rules</h3>
    <div className="form-row mt-2">
      <label htmlFor="rule-logic" className="col-form-label">
        Rule Logic:
      </label>
      <div className="col-auto">
        <select className="form-control" id="rule-logic" disabled={rules.length <= 1}>
          <option value="no-rule-logic" select={ruleLogic == null}>Select a rule logic</option>
          {RULE_LOGIC_OPTIONS.map((ruleLogicOption) => (
            <option value={ruleLogicOption.value} selected={ruleLogicOption.value === ruleLogic}>
              {ruleLogicOption.label}
            </option>
          ))}
        </select>
      </div>
    </div>
    <div className="form-group mt-2">
      {rules.map((rule, index) => <RuleField rule={rule} index={index} />)}
      <button type="button" className="btn btn-secondary btn-sm mt-2">Add Rule</button>
    </div>
  </div>
);
  /* eslint-enable jsx-a11y/label-has-associated-control */

RulesField.propTypes = {
  rules: PropTypes.arrayOf(RuleShape).isRequired,
  ruleLogic: PropTypes.string,
};
RulesField.defaultProps = {
  ruleLogic: null,
};

const formatTime = (hour, minute) => {
  const paddedHour = hour.toString().padStart(2, '0');
  const paddedMinute = minute.toString().padStart(2, '0');
  return `${paddedHour}:${paddedMinute}`;
};

const TimeSlotField = ({ timeSlot, index }) => {
  const dayId = `timeSlot-${index}-day`;
  const timeId = `timeSlot-${index}-time`;
  // I can't figure out how to make this pass and they do have an related control
  /* eslint-disable jsx-a11y/label-has-associated-control */
  return (
    <div className="form-row mt-2">
      <label htmlFor={dayId} className="col-form-label">
        Day of Week:
      </label>
      <div className="col-auto">
        <select className="form-control" id={dayId}>
          {DAYS_OF_THE_WEEK.map((day) => (
            <option value={day.value} selected={day.value === timeSlot.day}>{day.label}</option>
          ))}
        </select>
      </div>
      <label htmlFor={timeId} className="col-form-label">
        Time:
      </label>
      <div className="col-auto">
        <input
          type="text"
          className="form-control"
          id={timeId}
          value={formatTime(timeSlot.hour, timeSlot.minute)}
          required
        />
      </div>
      <div className="col-auto">
        <button type="button" className="btn btn-outline-danger btn-sm mt-1">Remove</button>
      </div>
    </div>
  );
  /* eslint-enable jsx-a11y/label-has-associated-control */
};

TimeSlotField.propTypes = {
  timeSlot: TimeSlotShape.isRequired,
  index: PropTypes.number.isRequired,
};

const TimeSlotsField = ({ timeSlots, timezone }) => (
  <div className="form-group">
    <h3>Meeting Times</h3>
    <StringField inputClassName="subscription-time-zone-input" field="timezone" label="Time Zone" value={timezone} />
    <div className="form-group mt-2">
      {timeSlots.map((timeSlot, index) => <TimeSlotField timeSlot={timeSlot} index={index} />)}
      <button type="button" className="btn btn-secondary btn-sm mt-2">Add Time Slot</button>
    </div>
  </div>
);

TimeSlotsField.propTypes = {
  timeSlots: PropTypes.arrayOf(TimeSlotShape).isRequired,
  timezone: PropTypes.string.isRequired,
};

const Subscription = () => {
  const [subscription, setSubscription] = React.useState(null);
  React.useEffect(() => {
    axios.get(`/v1/subscriptions/${getSubscriptionId()}`).then(
      (res) => { setSubscription(res.data); },
    );
  }, []);

  if (subscription == null) {
    return '';
  }

  return (
    <div className="container mt-2">
      <StringField field="name" label="Name" value={subscription.name} />
      <div className="form-row">
        <div className="col">
          <StringField field="location" label="Location" value={subscription.location} />
        </div>
        <div className="col">
          <StringField field="office" label="Office" value={subscription.office} />
        </div>
        <div className="col-2">
          <NumberField field="size" label="Size" value={subscription.size} />
        </div>
      </div>
      <RulesField rules={subscription.rules} ruleLogic={subscription.rule_logic} />
      <TimeSlotsField timeSlots={subscription.time_slots} timezone={subscription.timezone} />
      <button type="button" className="btn btn-primary mt-2">Update</button>
    </div>
  );
};

export default Subscription;
