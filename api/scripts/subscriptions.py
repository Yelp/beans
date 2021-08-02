import sys
from argparse import ArgumentParser
from argparse import Namespace
from datetime import datetime
from textwrap import indent
from typing import Tuple

import arrow
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from yelp_beans.logic.config import get_config
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import UserSubscriptionPreferences

DAY_STR_TO_WEEKDAY_NUMBER = {
    'Monday': 0,
    'Mon': 0,
    'Tuesday': 1,
    'Tue': 1,
    'Wednesday': 2,
    'Wed': 2,
    'Thursday': 3,
    'Thur': 3,
    'Friday': 4,
    'Fri': 4,
    'Saturday': 5,
    'Sat': 5,
    'Sunday': 6,
    'Sun': 6,
}

def create_session() -> Session:
    db_url = get_config().get('DATABASE_URL_PROD')
    if db_url is None:
        sys.exit('DATABASE_URL_PROD is not set in config.yaml, this is required to run this script')
    engine = create_engine(db_url)
    session_cls = sessionmaker(bind=engine)
    return session_cls()


def get_weekday_number(day: str) -> int:
    weekday = DAY_STR_TO_WEEKDAY_NUMBER.get(day)
    if weekday is None:
        valid_days = ', '.join(DAY_STR_TO_WEEKDAY_NUMBER.keys())
        sys.exit(f'Invalid day of the "{day}". Possible values are {valid_days}.')
    return weekday


def get_hour_minute(time_str: str) -> Tuple[int, int]:
    if ':' in time_str:
        hour_str, minute_str = time_str.split(':', maxsplit=1)
        hour = int(hour_str)
        minute = int(minute_str)
    else:
        hour = int(time_str)
        minute = 0

    return hour, minute


def parse_meeting_time(day: str, time_str: str, timezone_str: str) -> datetime:
    weekday = get_weekday_number(day)
    hour, minute = get_hour_minute(time_str)

    cur_time = arrow.now(timezone_str)
    result_time = cur_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    result_time = result_time.shift(weekday=weekday)

    return result_time.datetime


def create_subscription_entrypoint(args: Namespace) -> None:
    sub_datetimes = [
        SubscriptionDateTime(datetime=parse_meeting_time(day, time, args.timezone))
        for day, time in args.time
    ]
    rules = [Rule(name=field, value=value) for field, value in (args.rule or [])]

    subscription = MeetingSubscription(
        title=args.name,
        datetime=sub_datetimes,
        size=args.size,
        office=args.office,
        location=args.location,
        timezone=args.timezone,
        # Can only set this if there are rules
        rule_logic=args.rule_logic if rules else None,
        user_rules=rules,
    )

    datetimes_str = ', '.join((sub_datetime.datetime.isoformat() for sub_datetime in sub_datetimes))
    rules_str = ', '.join((f'{rule.name}={rule.value}' for rule in rules)) if rules else '(no rules)'
    values = (
        ('title', subscription.title),
        ('size', subscription.size),
        ('office', subscription.office),
        ('location', subscription.location),
        ('timezone', subscription.timezone),
        ('times', datetimes_str),
        ('rule logic', subscription.rule_logic),
        ('rules', rules_str),
    )
    values_str = indent('\n'.join((f'{field}: {value}' for field, value in values)), ' ' * 4)
    print(f'Subscription:\n{values_str}')

    resp = input('Create subscription (y/N): ')
    if resp == 'y':
        session = create_session()
        session.add(subscription)
        session.commit()
    else:
        print('Not creating subscription')


def remove_meet_time_entrypoint(args: Namespace) -> None:
    session = create_session()
    meet_sub = session.query(MeetingSubscription).options(
        joinedload(MeetingSubscription.datetime)
    ).filter(MeetingSubscription.title == args.name).one()
    weekday, time_str = args.time
    weekday_number = get_weekday_number(weekday)
    hour, minute = get_hour_minute(time_str)

    for meet_datetime in meet_sub.datetime:
        if all((
            meet_datetime.datetime.weekday() == weekday_number,
            meet_datetime.datetime.hour == hour,
            meet_datetime.datetime.minute == minute,
        )):
            session.query(UserSubscriptionPreferences).filter(
                UserSubscriptionPreferences.preference_id == meet_datetime.id
            ).delete()
            session.delete(meet_datetime)

    session.commit()

def add_create_arguments(parser: ArgumentParser) -> None:
    parser.add_argument('name', help='Name of the meeting subscription')
    parser.add_argument('-l', '--location', default='Online', help='Where in the office will the meeting will be held')
    parser.add_argument('-o', '--office', default='Remote', help='What office the meeting will be held in')
    parser.add_argument('-s', '--size', default=2, type=int, help='How many people per meeting')
    parser.add_argument(
        '-z',
        '--timezone',
        default='America/Los_Angeles',
        help='What timezone will the meeting be scheduled in',
    )
    parser.add_argument(
        '-t',
        '--time',
        metavar=('Weekday', 'Time'),
        nargs=2,
        action='append',
        required=True,
        help='When will the meetings be held. Can be specified multiple times. Example: -t Friday 14:30',
    )
    parser.add_argument(
        '-r',
        '--rule',
        metavar=('Field', 'Value'),
        nargs=2,
        action='append',
        help='What rules should be applied to this meeting. Example: -r work-email user@company.email',
    )
    parser.add_argument(
        '--rule-logic',
        default='any',
        choices=('any', 'all'),
        help='If user should match all or any of the rules (default: %(default)s)',
    )
    parser.set_defaults(func=create_subscription_entrypoint)


def add_remove_meet_time_parser_arguments(parser: ArgumentParser) -> None:
    parser.add_argument('name', help='Name of the meeting subscription')
    parser.add_argument(
        '-t',
        '--time',
        metavar=('Weekday', 'Time'),
        nargs=2,
        required=True,
        help='What meeting time to remove. Example: -t Friday 2PM',
    )
    parser.set_defaults(func=remove_meet_time_entrypoint)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser('create')
    add_create_arguments(create_parser)

    remove_meet_time_parser = subparsers.add_parser('remove_meeting_time')
    add_remove_meet_time_parser_arguments(remove_meet_time_parser)

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
