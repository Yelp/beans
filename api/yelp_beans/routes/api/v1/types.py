from __future__ import annotations

import enum
from typing import Literal

import arrow
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pytz import all_timezones
from pytz import utc

from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime


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
    model_config = ConfigDict(frozen=True)

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
    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_sqlalchemy(cls, model: Rule) -> RuleModel:
        return cls(field=model.name, value=model.value)


class NewSubscription(BaseModel):
    location: str = "Online"
    name: str = Field(min_length=1)
    office: str = "Remote"
    rule_logic: Literal["any", "all", None] = None
    rules: list[RuleModel] = Field(default_factory=list)
    size: int = Field(2, ge=2)
    time_slots: list[TimeSlot] = Field(min_length=1)
    timezone: str = "America/Los_Angeles"
    default_auto_opt_in: bool = False

    @field_validator("timezone")
    @classmethod
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
            default_auto_opt_in=model.default_auto_opt_in,
        )
