import logging
from typing import Any

from flask import Blueprint
from flask import jsonify
from flask import request

from yelp_beans.logic.subscription import apply_rules
from yelp_beans.logic.subscription import filter_subscriptions_by_user_data
from yelp_beans.logic.subscription import get_subscriber_counts
from yelp_beans.logic.subscription import get_subscription
from yelp_beans.logic.subscription import merge_subscriptions_with_preferences
from yelp_beans.logic.user import PreferenceOptions
from yelp_beans.logic.user import add_preferences
from yelp_beans.logic.user import get_user
from yelp_beans.logic.user import remove_preferences
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.api.v1.types import Subscription
from yelp_beans.routes.api.v1.types import TimeSlot

preferences_blueprint = Blueprint("preferences", __name__)


@preferences_blueprint.route("/", methods=["GET"])
def preferences_api():
    user = get_user(request.args.get("email"))
    if not user:
        resp = jsonify([])
        resp.status_code = 200
        return resp

    subscriptions = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(subscriptions, user)

    resp = jsonify(subscriptions)
    resp.status_code = 200
    return resp


@preferences_blueprint.route("/subscription/<int:subscription_id>", methods=["POST"])
def preferences_api_post(subscription_id: int) -> str:
    data = request.json
    user = get_user(data.get("email"))
    del data["email"]
    if not user:
        return "400"

    form_selection = {}
    for key, value in data.items():
        # Convert key (a table id) to an int
        form_selection[int(key)] = value

    removed = remove_preferences(user, form_selection, subscription_id)
    logging.info("Removed")
    logging.info(removed)

    added = add_preferences(user, form_selection, subscription_id)
    logging.info("Added")
    logging.info(added)

    return "OK"


def update_auto_opt_in(user_prefs: list[UserSubscriptionPreferences], auto_opt_in: bool | None) -> None:
    for matching_pref in user_prefs:
        if auto_opt_in is not None and matching_pref.auto_opt_in != auto_opt_in:
            matching_pref.auto_opt_in = auto_opt_in


@preferences_blueprint.route("/subscribe/<int:subscription_id>", methods=["POST"])
def subscribe_api_post(subscription_id: int) -> dict[str, Any]:
    data = request.json
    user = get_user(data.get("email"))
    auto_opt_in: bool | None = data.get("auto_opt_in")
    time_slot_data: str | None = data.get("time_slot")
    if not user:
        resp = jsonify({"msg": f"A user doesn't exist with the email of \"{data.get('email')}\""})
        resp.status_code = 400
        return resp

    subscription = get_subscription(subscription_id)
    approved = apply_rules(user, subscription, subscription.user_rules)
    if not approved:
        resp = jsonify({"msg": "You are not eligible for this subscription"})
        resp.status_code = 403
        return resp

    if time_slot_data is None:
        datetime_to_subscriber_counts = get_subscriber_counts(subscription_id)
        if datetime_to_subscriber_counts:
            datetime_id, _ = max(datetime_to_subscriber_counts.items(), key=lambda row: row[1])
        else:
            # No most popular time slot, so just pick the first one
            datetime_id = subscription.datetime[0].id
    else:
        datetime_id = None
        time_slot = TimeSlot.parse_obj(time_slot_data)
        for sub_datetime in subscription.datetime:
            sub_time_slot = TimeSlot.from_sqlalchemy(sub_datetime, subscription.timezone)
            if sub_time_slot == time_slot:
                datetime_id = sub_datetime.id
                break

        if datetime_id is None:
            resp = jsonify({"msg": f"Unable to find subscription datetime from time slot {time_slot}"})
            resp.status_code = 400
            return resp

    assert datetime_id is not None, "We shouldn't get to this point without picking a datetime"

    subscription_user_prefs = [pref for pref in user.subscription_preferences if pref.subscription_id == subscription_id]

    time_slot_prefs = [pref for pref in subscription_user_prefs if pref.preference_id == datetime_id]

    if time_slot_data is None and subscription_user_prefs:
        update_auto_opt_in(subscription_user_prefs, auto_opt_in)
        new_preference = False
    elif time_slot_prefs:
        update_auto_opt_in(time_slot_prefs, auto_opt_in)
        new_preference = False
    else:
        preference = PreferenceOptions(active=True)
        if auto_opt_in is not None:
            preference["auto_opt_in"] = auto_opt_in
        add_preferences(user, {datetime_id: preference}, subscription_id)
        new_preference = True

    # get_subscriber_counts return this datetime id, so it should always exist in subscription.datetime
    datetime = next(rule for rule in subscription.datetime if rule.id == datetime_id)
    return {
        "subscription": Subscription.from_sqlalchemy(subscription).model_dump(mode="json"),
        "time_slot": TimeSlot.from_sqlalchemy(datetime, subscription.timezone).model_dump(mode="json"),
        "new_preference": new_preference,
    }
