export const addUUID = (array) =>
  array.map((item) => {
    const newItem = { ...item };
    newItem.uuid = crypto.randomUUID();
    return newItem;
  });

export const removeUUID = (array) =>
  array.map((item) => {
    const { uuid, ...remainingFields } = item;
    return remainingFields;
  });

export const prepareSubscriptionPayload = (subscription) => {
  const payloadSubscription = { ...subscription };
  payloadSubscription.rules = removeUUID(payloadSubscription.rules);
  payloadSubscription.time_slots = removeUUID(payloadSubscription.time_slots);
  // we don't require setting the rule logic if there is only rule because all vs any doesn't
  // change anything if there is one rule. On the backend we require that we set, so default
  // to all in that case
  if (
    payloadSubscription.rules.length === 1 &&
    payloadSubscription.rule_logic == null
  ) {
    payloadSubscription.rule_logic = "all";
  }
  return payloadSubscription;
};
