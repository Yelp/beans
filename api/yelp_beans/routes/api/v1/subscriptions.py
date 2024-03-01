from __future__ import annotations

import json
from datetime import datetime

import arrow
from database import db
from flask import Blueprint
from flask import jsonify
from flask import request
from pydantic import ValidationError

from yelp_beans.logic.subscription import get_subscription as get_subscription_model
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.routes.api.v1.types import NewSubscription
from yelp_beans.routes.api.v1.types import RuleModel
from yelp_beans.routes.api.v1.types import Subscription
from yelp_beans.routes.api.v1.types import TimeSlot

subscriptions_blueprint = Blueprint("subscriptions", __name__)


def calculate_meeting_datetime(time_slot: TimeSlot, timezone_str: str) -> datetime:
    cur_time = arrow.now(timezone_str)
    result_time = cur_time.replace(hour=time_slot.hour, minute=time_slot.minute, second=0, microsecond=0)
    result_time = result_time.shift(weekday=time_slot.day.to_day_number())
    result_time = result_time.to("utc")

    return result_time.datetime


@subscriptions_blueprint.route("/", methods=["POST"])
def create_subscription():
    try:
        data = NewSubscription.parse_obj(request.get_json())
    except ValidationError as e:
        # There is probably a better way to do this, but not sure what it is yet
        resp = jsonify(json.loads(e.json()))
        resp.status_code = 400
        return resp

    sub_datetimes = [
        SubscriptionDateTime(datetime=calculate_meeting_datetime(time_slot, data.timezone)) for time_slot in data.time_slots
    ]
    rules = [Rule(name=rule.field, value=rule.value) for rule in data.rules]

    subscription = MeetingSubscription(
        title=data.name,
        datetime=sub_datetimes,
        size=data.size,
        office=data.office,
        location=data.location,
        timezone=data.timezone,
        # Can only set this if there are rules
        rule_logic=data.rule_logic if rules else None,
        user_rules=rules,
        default_auto_opt_in=data.default_auto_opt_in,
    )

    db.session.add(subscription)
    db.session.commit()

    resp = jsonify(id=subscription.id)
    resp.status_code = 200
    return resp


@subscriptions_blueprint.route("/", methods=["GET"])
def get_subscriptions():
    spec_models = MeetingSubscription.query.all()
    specs = [Subscription.from_sqlalchemy(model) for model in spec_models]
    # There is probably a better way to do this, but not sure what it is yet
    resp = jsonify([json.loads(spec.json()) for spec in specs])
    resp.status_code = 200
    return resp


@subscriptions_blueprint.route("/<int:sub_id>", methods=["GET"])
def get_subscription(sub_id: int):
    sub_model = get_subscription_model(sub_id)
    sub = Subscription.from_sqlalchemy(sub_model)
    # There is probably a better way to do this, but not sure what it is yet
    resp = jsonify(json.loads(sub.json()))
    resp.status_code = 200
    return resp


@subscriptions_blueprint.route("/<int:sub_id>", methods=["PUT"])
def update_subscription(sub_id: int):
    sub_model = MeetingSubscription.query.filter(MeetingSubscription.id == sub_id).one()
    try:
        data = NewSubscription.parse_obj(request.get_json())
    except ValidationError as e:
        # There is probably a better way to do this, but not sure what it is yet
        resp = jsonify(json.loads(e.json()))
        resp.status_code = 400
        return resp

    sub_model.title = data.name
    sub_model.size = data.size
    sub_model.office = data.office
    sub_model.location = data.location
    sub_model.timezone = data.timezone
    sub_model.default_auto_opt_in = data.default_auto_opt_in
    sub_model.rule_logic = data.rule_logic if data.rules else None

    existing_rules = {RuleModel.from_sqlalchemy(r): r for r in sub_model.user_rules}
    for rule in data.rules:
        if rule in existing_rules:
            del existing_rules[rule]
        else:
            sub_model.user_rules.append(Rule(name=rule.field, value=rule.value))

    # Remaining rules weren't in the list of updated rules
    for rule in existing_rules.values():
        sub_model.user_rules.remove(rule)

    # To account for daylight savings we have to make sure the utc datetimes
    # are being compared at the same time of year
    def normalize_datetime(dt: SubscriptionDateTime) -> tuple[int, int, int]:
        time_slot = TimeSlot.from_sqlalchemy(dt, sub_model.timezone)
        normalized = calculate_meeting_datetime(time_slot, sub_model.timezone)
        # We only care that the weekday, hour, and minute now that we have normalized it
        return (normalized.weekday(), normalized.hour, normalized.minute)

    existing_datetimes = {normalize_datetime(ts): ts for ts in sub_model.datetime}

    for time_slot in data.time_slots:
        # we have to compare based on the meeting datetime, so that the timezone
        # being changed is accounted for since we store utc
        time_slot_dt = calculate_meeting_datetime(time_slot, data.timezone)
        time_slot_key = (time_slot_dt.weekday(), time_slot_dt.hour, time_slot_dt.minute)
        if time_slot_key in existing_datetimes:
            del existing_datetimes[time_slot_key]
        else:
            sub_model.datetime.append(SubscriptionDateTime(datetime=time_slot_dt))

    # Remaining datetimes weren't in the list of updated time_slots
    for dt in existing_datetimes.values():
        sub_model.datetime.remove(dt)

    db.session.commit()

    resp = jsonify({})
    resp.status_code = 200
    return resp
