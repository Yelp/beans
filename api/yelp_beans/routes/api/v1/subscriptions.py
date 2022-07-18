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


class TimeSlot(BaseModel):
    day: Weekday
    hour: int
    minute: int = 0


class RuleModel(BaseModel):
    field: str
    value: str


class NewSubscription(BaseModel):
    location: str = 'Online'
    name: str
    office: str = 'Remote'
    rule_logic: Literal['any', 'all'] = 'any'
    rules: List[RuleModel] = ()
    size: int = 2
    time_slots: List[TimeSlot]
    timezone: str = 'America/Los_Angeles'


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
