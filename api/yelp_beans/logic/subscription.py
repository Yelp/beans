from datetime import datetime
from datetime import timedelta

from database import db
from pytz import timezone
from pytz import utc
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription


def filter_subscriptions_by_user_data(subscriptions, user):
    approved_subscriptions = []
    for subscription in subscriptions:
        subscription_rules = MeetingSubscription.query.filter(
            MeetingSubscription.id == subscription['id']).one().user_rules

        approved = apply_rules(user, subscription, subscription_rules)
        if approved is not None:
            approved_subscriptions.append(approved)
    return approved_subscriptions


def apply_rules(user, subscription, subscription_rules):
    """
    Apply logic to rules set for each subscription.  In a way this authorizes who can
    see the subscription.  Rules can be applied in two ways:  All rules must apply and
    some rules must apply.

    user: models.User()
    subscription: Union[models.MeetingSubscription(), Dict[str, Any]]
    subscription_rules: models.Rule()
    """
    if isinstance(subscription, dict):
        rule_logic_str = subscription.get('rule_logic')
    else:
        rule_logic_str = subscription.rule_logic

    if rule_logic_str == 'any':
        assert subscription_rules, 'You created logic for rules but don\'t have any rules!'
        rule_logic = any
    elif rule_logic_str == 'all':
        assert subscription_rules, 'You created logic for rules but don\'t have any rules!'
        rule_logic = all
    else:
        return subscription

    rules = set()
    for rule in subscription_rules:
        user_rule = user.meta_data[rule.name]
        subscription_rule = rule.value
        if type(user_rule) is list:
            rules.add(subscription_rule in user_rule)
        else:
            rules.add(user_rule == subscription_rule)

    if rule_logic(rules):
        return subscription

    return None


def merge_subscriptions_with_preferences(user):
    user_preferences = [
        {
            'subscription_id': user_subscription.subscription_id,
            'datetime_id': user_subscription.preference_id
        } for user_subscription in user.subscription_preferences
    ]
    subscriptions = [
        {
            'id': subscription.id,
            'title': subscription.title,
            'office': subscription.office,
            'location': subscription.location,
            'size': subscription.size,
            'timezone': subscription.timezone,
            'rule_logic': subscription.rule_logic,
            'datetime': get_subscription_dates(subscription),
        } for subscription in MeetingSubscription.query.all()
    ]
    for subscription in subscriptions:
        for user_preference in user_preferences:
            if subscription['id'] == user_preference['subscription_id']:
                for date in subscription['datetime']:
                    if date['id'] == user_preference['datetime_id']:
                        date['active'] = True

    return subscriptions


def get_subscription_dates(subscription):
    dates = [
        {
            'id': date.id,
            'date': date.datetime.replace(tzinfo=utc).isoformat(),
            'active': False
        }
        for date in subscription.datetime
    ]
    # Return a sorted list so that it is sorted on the frontend
    return sorted(dates, key=lambda i: i['date'])


def get_specs_from_subscription(subscription):
    specs = []
    for subscription_datetime in subscription.datetime:
        subscription_tz = timezone(subscription.timezone)
        week_start = datetime.now(subscription_tz) - timedelta(days=datetime.now(subscription_tz).weekday())
        week_start = week_start.replace(
            hour=0, minute=0, second=0, microsecond=0)

        subscription_dt = subscription_datetime.datetime.replace(tzinfo=utc).astimezone(subscription_tz)
        week_iter = week_start
        while week_iter.weekday() != subscription_dt.weekday():
            week_iter += timedelta(days=1)

        meeting_datetime = week_iter.replace(
            hour=subscription_dt.hour, minute=subscription_dt.minute
        ).astimezone(utc)

        specs.append(MeetingSpec(meeting_subscription=subscription, datetime=meeting_datetime))
    return week_start, specs


def store_specs_from_subscription(subscription, week_start, specs):
    """
    Idempotent function to store meeting specs for this week.
    """
    current_specs = MeetingSpec.query.filter(
        MeetingSpec.meeting_subscription_id == subscription.id,
        MeetingSpec.datetime > week_start
    ).all()

    if current_specs:
        return

    db.session.add_all(specs)
    db.session.commit()
    return specs
