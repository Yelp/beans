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
from pydantic import Field
from pydantic import ValidationError
from pydantic import validator
from pytz import all_timezones
from pytz import utc
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
    hour: int = Field(ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)

    class Config:
        frozen = True

    @classmethod
    def from_sqlalchemy(cls, model: SubscriptionDateTime, timezone: str) -> RuleModel:
        tz_time = arrow.get(model.datetime.replace(tzinfo=utc)).to(timezone)
        return cls(
            day=Weekday.from_day_number(model.datetime.weekday()),
            hour=tz_time.hour,
            minute=tz_time.minute,
        )


class RuleModel(BaseModel):
    field: str
    value: str

    class Config:
        frozen = True

    @classmethod
    def from_sqlalchemy(cls, model: Rule) -> RuleModel:
        return cls(field=model.name, value=model.value)


class NewSubscription(BaseModel):
    location: str = 'Online'
    name: str = Field(min_lenth=1)
    office: str = 'Remote'
    rule_logic: Literal['any', 'all', None] = None
    rules: List[RuleModel] = Field(default_factory=list)
    size: int = Field(2, ge=2)
    time_slots: List[TimeSlot] = Field(min_items=1)
    timezone: str = 'America/Los_Angeles'

    @validator('timezone')
    def is_valid_timezone(cls, value: str) -> str:
        if value not in all_timezones:
            raise ValueError(f"{value} is not a valid timezone")
        return value


class Subscription(NewSubscription):
    id: int

    @classmethod
    def from_sqlalchemy(cls, model: MeetingSubscription) -> Subscription:
        rules = [RuleModel.from_sqlalchemy(rule) for rule in model.user_rules]
        time_slots = [TimeSlot.from_sqlalchemy(time_slot, model.timezone) for time_slot in model.datetime]
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
    result_time = result_time.to('utc')

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


@subscriptions_blueprint.route('/<int:sub_id>', methods=["PUT"])
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

    resp = jsonify()
    resp.status_code = 200
    return resp
