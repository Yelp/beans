from __future__ import annotations

import enum
import json
from datetime import datetime
from typing import List
from typing import Literal

import arrow
from database import db
from flask import Blueprint
from flask import jsonify
from flask import request
from pydantic import BaseModel
from pydantic import ValidationError
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime

subscriptions_blueprint = Blueprint('subscriptions', __name__)


@enum.unique
class Weekday(enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    def to_day_number(self) -> int:
        day_to_number = {
            Weekday.MONDAY: 0,
            Weekday.TUESDAY: 1,
            Weekday.WEDNESDAY: 2,
            Weekday.THURSDAY: 3,
            Weekday.FRIDAY: 4,
            Weekday.SATURDAY: 5,
            Weekday.SUNDAY: 6,
        }
        return day_to_number[self]

    @staticmethod
    def from_day_number(day_number: int) -> Weekday:
        for day in Weekday:
            if day_number == day.to_day_number():
                return day
        raise ValueError(f"No day for day number of {day_number}")


class TimeSlot(BaseModel):
    day: Weekday
    hour: int
    minute: int = 0

    @classmethod
    def from_sqlalchemy(cls, model: SubscriptionDateTime) -> RuleModel:
        return cls(
            day=Weekday.from_day_number(model.datetime.weekday()),
            hour=model.datetime.hour,
            minute=model.datetime.minute,
        )


class RuleModel(BaseModel):
    field: str
    value: str

    @classmethod
    def from_sqlalchemy(cls, model: Rule) -> RuleModel:
        return cls(field=model.name, value=model.value)


class NewSubscription(BaseModel):
    location: str = 'Online'
    name: str
    office: str = 'Remote'
    rule_logic: Literal['any', 'all', None] = None
    rules: List[RuleModel] = ()
    size: int = 2
    time_slots: List[TimeSlot]
    timezone: str = 'America/Los_Angeles'


class Subscription(NewSubscription):
    id: int

    @classmethod
    def from_sqlalchemy(cls, model: MeetingSubscription) -> Subscription:
        rules = [RuleModel.from_sqlalchemy(rule) for rule in model.user_rules]
        time_slots = [TimeSlot.from_sqlalchemy(time_slot) for time_slot in model.datetime]
        return cls(
            id=model.id,
            location=model.location,
            name=model.title,
            office=model.office,
            rule_logic=model.rule_logic,
            rules=rules,
            size=model.size,
            time_slots=time_slots,
            timezone=model.timezone,
        )


def calculate_meeting_datetime(time_slot: TimeSlot, timezone_str: str) -> datetime:
    cur_time = arrow.now(timezone_str)
    result_time = cur_time.replace(hour=time_slot.hour, minute=time_slot.minute, second=0, microsecond=0)
    result_time = result_time.shift(weekday=time_slot.day.to_day_number())

    return result_time.datetime


@subscriptions_blueprint.route('/', methods=["POST"])
def create_subscription():
    try:
        data = NewSubscription.parse_obj(request.get_json())
    except ValidationError as e:
        # There is probably a better way to do this, but not sure what it is yet
        resp = jsonify(json.loads(e.json()))
        resp.status_code = 400
        return resp

    sub_datetimes = [
        SubscriptionDateTime(datetime=calculate_meeting_datetime(time_slot, data.timezone))
        for time_slot in data.time_slots
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
    )

    db.session.add(subscription)
    db.session.commit()

    resp = jsonify(id=subscription.id)
    resp.status_code = 200
    return resp


@subscriptions_blueprint.route('/', methods=["GET"])
def get_subscriptions():
    spec_models = MeetingSubscription.query.all()
    specs = [Subscription.from_sqlalchemy(model) for model in spec_models]
    # There is probably a better way to do this, but not sure what it is yet
    resp = jsonify([json.loads(spec.json()) for spec in specs])
    resp.status_code = 200
    return resp


@subscriptions_blueprint.route('/<int:sub_id>', methods=["GET"])
def get_subscription(sub_id: int):
    sub_model = MeetingSubscription.query.filter(MeetingSubscription.id == sub_id).one()
    sub = Subscription.from_sqlalchemy(sub_model)
    # There is probably a better way to do this, but not sure what it is yet
    resp = jsonify(json.loads(sub.json()))
    resp.status_code = 200
    return resp
