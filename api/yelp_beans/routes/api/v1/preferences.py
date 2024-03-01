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
from yelp_beans.logic.user import add_preferences
from yelp_beans.logic.user import get_user
from yelp_beans.logic.user import remove_preferences
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


@preferences_blueprint.route("/subscribe/<int:subscription_id>", methods=["POST"])
def subscribe_api_post(subscription_id: int) -> dict[str, Any]:
    data = request.json
    user = get_user(data.get("email"))
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

    datetime_to_subscriber_counts = get_subscriber_counts(subscription_id)
    if datetime_to_subscriber_counts:
        best_datetime_id, _ = max(datetime_to_subscriber_counts.items(), key=lambda row: row[1])
    else:
        # No most popular time slot, so just pick the first one
        best_datetime_id = subscription.datetime[0].id

    existing_matching_prefs = [pref for pref in user.subscription_preferences if pref.subscription_id == subscription_id]

    if existing_matching_prefs:
        new_preference = False
    else:
        add_preferences(user, {best_datetime_id: {"active": True}}, subscription_id)
        new_preference = True

    # get_subscriber_counts return this datetime id, so it should always exist in subscription.datetime
    datetime = next(rule for rule in subscription.datetime if rule.id == best_datetime_id)
    return {
        "subscription": Subscription.from_sqlalchemy(subscription).model_dump(mode="json"),
        "time_slot": TimeSlot.from_sqlalchemy(datetime, subscription.timezone).model_dump(mode="json"),
        "new_preference": new_preference,
    }
