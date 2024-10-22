import React from "react";
import PropTypes from "prop-types";

const DAYS_OF_THE_WEEK = [
  { label: "Sunday", value: "sunday" },
  { label: "Monday", value: "monday" },
  { label: "Tuesday", value: "tuesday" },
  { label: "Wednesday", value: "wednesday" },
  { label: "Thursday", value: "thursday" },
  { label: "Friday", value: "friday" },
  { label: "Saturday", value: "saturday" },
];

const RULE_LOGIC_OPTIONS = [
  { label: "all rules", value: "all" },
  { label: "at least one rule", value: "any" },
];

const RuleShape = PropTypes.shape({
  field: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  uuid: PropTypes.string.isRequired,
});
const TimeSlotShape = PropTypes.shape({
  day: PropTypes.string.isRequired,
  hour: PropTypes.number.isRequired,
  minute: PropTypes.number.isRequired,
  uuid: PropTypes.string.isRequired,
});

const SubscriptionShape = PropTypes.shape({
  location: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  office: PropTypes.string.isRequired,
  rule_logic: PropTypes.string.isRequired,
  rules: PropTypes.arrayOf(RuleShape).isRequired,
  size: PropTypes.number.isRequired,
  time_slots: PropTypes.arrayOf(TimeSlotShape).isRequired,
  timezone: PropTypes.string.isRequired,
  default_auto_opt_in: PropTypes.bool.isRequired,
});

function StringField({ field, label, value, inputClassName, updateField }) {
  return (
    <div className="form-group">
      <label htmlFor={field}>{label}</label>
      <input
        type="text"
        className={`form-control ${inputClassName}`}
        id={field}
        value={value}
        onChange={(e) => updateField(field, e.target.value)}
        required
      />
    </div>
  );
}

StringField.propTypes = {
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  inputClassName: PropTypes.string,
  updateField: PropTypes.func.isRequired,
};

StringField.defaultProps = {
  inputClassName: "",
};

function DefaultAutoOptInField({ field, label, value, updateField }) {
  return (
    <div className="form-group">
      <label htmlFor={field}>{label}</label>
      <select
        className="form-control"
        id={field}
        value={value}
        onChange={(e) => updateField(field, e.target.value === "true")}
      >
        <option key="true" value="true">
          True
        </option>
        <option key="false" value="false">
          False
        </option>
      </select>
    </div>
  );
}

DefaultAutoOptInField.propTypes = {
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.bool.isRequired,
  updateField: PropTypes.func.isRequired,
};

function NumberField({ field, label, value, updateField, min }) {
  return (
    <div className="form-group">
      <label htmlFor={field}>{label}</label>
      <input
        type="number"
        min={min}
        className="form-control"
        id={field}
        value={value}
        onChange={(e) => updateField(field, e.target.value)}
        required
      />
    </div>
  );
}

NumberField.propTypes = {
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  updateField: PropTypes.func.isRequired,
  min: PropTypes.number,
};
NumberField.defaultProps = {
  min: null,
};

function RuleField({ rule, updateRule, removeRule }) {
  const ruleFieldId = `rule-${rule.uuid}-field`;
  const ruleValueId = `rule-${rule.uuid}-value`;
  // I can't figure out how to make this pass and they do have an related control
  /* eslint-disable jsx-a11y/label-has-associated-control */
  return (
    <div className="form-row mt-2">
      <label htmlFor={ruleFieldId} className="col-form-label">
        Field:
      </label>
      <div className="col">
        <input
          type="text"
          className="form-control"
          id={ruleFieldId}
          value={rule.field}
          onChange={(e) => updateRule(rule.uuid, "field", e.target.value)}
          required
        />
      </div>
      <label htmlFor={ruleValueId} className="col-form-label">
        Value:
      </label>
      <div className="col">
        <input
          type="text"
          className="form-control"
          id={ruleValueId}
          value={rule.value}
          onChange={(e) => updateRule(rule.uuid, "value", e.target.value)}
          required
        />
      </div>
      <div className="col-auto">
        <button
          type="button"
          className="btn btn-outline-danger btn-sm mt-1"
          onClick={() => removeRule(rule.uuid)}
        >
          Remove
        </button>
      </div>
    </div>
  );
  /* eslint-enable jsx-a11y/label-has-associated-control */
}

RuleField.propTypes = {
  rule: RuleShape.isRequired,
  updateRule: PropTypes.func.isRequired,
  removeRule: PropTypes.func.isRequired,
};

// I can't figure out how to make this pass and they do have an related control
/* eslint-disable jsx-a11y/label-has-associated-control */
function RulesField({ rules, ruleLogic, updateField }) {
  const addRule = () =>
    updateField("rules", (existRules) => {
      const newRules = existRules.slice();
      newRules.push({ uuid: crypto.randomUUID(), field: "", value: "" });
      return newRules;
    });

  const updateRule = (uuid, field, value) => {
    updateField("rules", (existRules) =>
      existRules.map((rule) => {
        if (rule.uuid !== uuid) {
          return rule;
        }
        const newRule = { ...rule };
        newRule[field] = value;
        return newRule;
      }),
    );
  };
  const removeRule = (uuid) => {
    updateField("rules", (existRules) =>
      existRules.filter((rule) => rule.uuid !== uuid),
    );
  };

  return (
    <div className="form-group">
      <h3>Rules</h3>
      <div className="form-row mt-2">
        <label htmlFor="rule-logic" className="col-form-label">
          Must match
        </label>
        <div className="col-auto">
          <select
            className="form-control"
            id="rule-logic"
            value={ruleLogic}
            disabled={rules.length <= 1}
            onChange={(e) => updateField("rule_logic", e.target.value)}
          >
            <option value={null}>Select a rule logic</option>
            {RULE_LOGIC_OPTIONS.map((ruleLogicOption) => (
              <option value={ruleLogicOption.value} key={ruleLogicOption.value}>
                {ruleLogicOption.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="form-group mt-2">
        {rules.map((rule) => (
          <RuleField
            key={rule.uuid}
            rule={rule}
            updateRule={updateRule}
            removeRule={removeRule}
          />
        ))}
        <button
          type="button"
          className="btn btn-secondary btn-sm mt-2"
          onClick={addRule}
        >
          Add Rule
        </button>
      </div>
    </div>
  );
}
/* eslint-enable jsx-a11y/label-has-associated-control */

RulesField.propTypes = {
  rules: PropTypes.arrayOf(RuleShape).isRequired,
  ruleLogic: PropTypes.string,
  updateField: PropTypes.func.isRequired,
};
RulesField.defaultProps = {
  ruleLogic: null,
};

const formatTime = (hour, minute) => {
  const paddedHour = hour.toString().padStart(2, "0");
  const paddedMinute = minute.toString().padStart(2, "0");
  return `${paddedHour}:${paddedMinute}`;
};

function TimeSlotField({ timeSlot, updateTimeSlot, removeTimeSlot }) {
  const dayId = `timeSlot-${timeSlot.uuid}-day`;
  const timeId = `timeSlot-${timeSlot.uuid}-time`;
  const [time, setTime] = React.useState(
    formatTime(timeSlot.hour, timeSlot.minute),
  );
  const [timeError, setTimeError] = React.useState(null);

  React.useEffect(() => {
    const parts = time.split(":");
    // Default to invalid value, so update doesn't work if there is a bad string
    let hour = -1;
    let minute = -1;
    if (parts.length === 2) {
      const [strHour, strMinute] = parts;
      const parsedHour = parseInt(strHour, 10);
      const parsedMinute = parseInt(strMinute, 10);
      if (Number.isNaN(parsedHour) || Number.isNaN(parsedMinute)) {
        setTimeError("Couldn't parse hour and/or minute as a number");
      } else {
        setTimeError(null);
        hour = parsedHour;
        minute = parsedMinute;
      }
    } else {
      setTimeError("Invalid Time format. Must be HH:MM");
    }

    updateTimeSlot(timeSlot.uuid, "hour", hour);
    updateTimeSlot(timeSlot.uuid, "minute", minute);
  }, [time]);
  // I can't figure out how to make this pass and they do have an related control
  /* eslint-disable jsx-a11y/label-has-associated-control */
  return (
    <div className="form-row mt-2">
      <label htmlFor={dayId} className="col-form-label">
        Day of Week:
      </label>
      <div className="col-auto">
        <select
          className="form-control"
          id={dayId}
          value={timeSlot.day}
          onChange={(e) => updateTimeSlot(timeSlot.uuid, "day", e.target.value)}
        >
          {DAYS_OF_THE_WEEK.map((day) => (
            <option value={day.value} key={day.value}>
              {day.label}
            </option>
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
          value={time}
          onChange={(e) => setTime(e.target.value)}
          required
        />
      </div>
      {timeError && (
        <div className="col-auto d-flex align-items-center text-danger small">
          {timeError}
        </div>
      )}
      <div className="col-auto">
        <button
          type="button"
          className="btn btn-outline-danger btn-sm mt-1"
          onClick={() => removeTimeSlot(timeSlot.uuid)}
        >
          Remove
        </button>
      </div>
    </div>
  );
  /* eslint-enable jsx-a11y/label-has-associated-control */
}

TimeSlotField.propTypes = {
  timeSlot: TimeSlotShape.isRequired,
  updateTimeSlot: PropTypes.func.isRequired,
  removeTimeSlot: PropTypes.func.isRequired,
};

function TimeSlotsField({ timeSlots, timezone, updateField }) {
  const addTimeSlot = () =>
    updateField("time_slots", (existTimeSlots) => {
      const newTimeSlots = existTimeSlots.slice();
      newTimeSlots.push({
        uuid: crypto.randomUUID(),
        day: "monday",
        hour: 0,
        minute: 0,
      });
      return newTimeSlots;
    });
  const updateTimeSlot = (uuid, field, value) => {
    updateField("time_slots", (existTimeSlots) =>
      existTimeSlots.map((timeSlot) => {
        if (timeSlot.uuid !== uuid) {
          return timeSlot;
        }
        const newtimeSlot = { ...timeSlot };
        newtimeSlot[field] = value;
        return newtimeSlot;
      }),
    );
  };
  const removeTimeSlot = (uuid) => {
    updateField("time_slots", (existTimeSlots) =>
      existTimeSlots.filter((timeSlot) => timeSlot.uuid !== uuid),
    );
  };

  return (
    <div className="form-group">
      <h3>Meeting Times</h3>
      <StringField
        inputClassName="subscription-time-zone-input"
        field="timezone"
        label="Time Zone"
        value={timezone}
        updateField={updateField}
      />
      <div className="form-group mt-2">
        {timeSlots.map((timeSlot) => (
          <TimeSlotField
            key={timeSlot.uuid}
            timeSlot={timeSlot}
            updateTimeSlot={updateTimeSlot}
            removeTimeSlot={removeTimeSlot}
          />
        ))}
        <button
          type="button"
          className="btn btn-secondary btn-sm mt-2"
          onClick={addTimeSlot}
        >
          Add Time Slot
        </button>
      </div>
    </div>
  );
}

TimeSlotsField.propTypes = {
  timeSlots: PropTypes.arrayOf(TimeSlotShape).isRequired,
  timezone: PropTypes.string.isRequired,
  updateField: PropTypes.func.isRequired,
};

function EditSubscription({ subscription, setSubscription }) {
  const updateField = (field, newValue) => {
    setSubscription((oldConfig) => {
      const newConfig = { ...oldConfig };
      if (newValue instanceof Function) {
        newConfig[field] = newValue(newConfig[field]);
      } else {
        newConfig[field] = newValue;
      }
      return newConfig;
    });
  };

  return (
    <div>
      <StringField
        field="name"
        label="Name"
        value={subscription.name}
        updateField={updateField}
      />
      <div className="form-row">
        <div className="col">
          <StringField
            field="location"
            label="Location"
            value={subscription.location}
            updateField={updateField}
          />
        </div>
        <div className="col">
          <StringField
            field="office"
            label="Office"
            value={subscription.office}
            updateField={updateField}
          />
        </div>
        <div className="col-2">
          <NumberField
            field="size"
            label="Size"
            min={2}
            value={subscription.size}
            updateField={updateField}
          />
        </div>
        <div className="col-2">
          <DefaultAutoOptInField
            field="default_auto_opt_in"
            label="Default Auto Opt-In"
            value={subscription.default_auto_opt_in}
            updateField={updateField}
          />
        </div>
      </div>
      <RulesField
        rules={subscription.rules}
        ruleLogic={subscription.rule_logic}
        updateField={updateField}
      />
      <TimeSlotsField
        timeSlots={subscription.time_slots}
        timezone={subscription.timezone}
        updateField={updateField}
      />
    </div>
  );
}

EditSubscription.propTypes = {
  subscription: SubscriptionShape.isRequired,
  setSubscription: PropTypes.func.isRequired,
};

export default EditSubscription;
