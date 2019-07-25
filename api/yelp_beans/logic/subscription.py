# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

from google.appengine.ext import ndb
from google.appengine.ext.db import NeedIndexError
from pytz import utc
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription


def filter_subscriptions_by_user_data(subscriptions, user):
    approved_subscriptions = []
    for subscription in subscriptions:
        subscription_rules = ndb.Key(urlsafe=subscription['id']).get().user_rules

        if subscription.get('rule_logic') == 'any':
            assert subscription_rules, 'You created logic for rules but don\'t have any rules!'
            approved = apply_rules(user, subscription, subscription_rules, any)
        elif subscription.get('rule_logic') == 'all':
            assert subscription_rules, 'You created logic for rules but don\'t have any rules!'
            approved = apply_rules(user, subscription, subscription_rules, all)
        else:
            approved = subscription

        if approved is not None:
            approved_subscriptions.append(approved)
    return approved_subscriptions


def apply_rules(user, subscription, subscription_rules, rule_logic):
    """
    Apply logic to rules set for each subscription.  In a way this authorizes who can
    see the subscription.  Rules can be applied in two ways:  All rules must apply and
    some rules must apply.

    user: models.User()
    subscription: models.MeetingSubscription()
    subscription_rules: models.Rule()
    rule_logic: all(), any()
    """
    rules = {
        user.metadata.get(rule.get().name) == rule.get().value
        for rule in subscription_rules
    }
    if rule_logic(rules):
        return subscription

    return None


def merge_subscriptions_with_preferences(user):
    user_preferences = [
        {
            'subscription_id': user_subscription.get().subscription.urlsafe(),
            'datetime_id': user_subscription.get().preference.urlsafe()
        } for user_subscription in user.subscription_preferences
    ]
    subscriptions = [
        {
            'id': subscription.key.urlsafe(),
            'title': subscription.title,
            'office': subscription.office,
            'location': subscription.location,
            'size': subscription.size,
            'timezone': subscription.timezone,
            'rule_logic': subscription.rule_logic,
            'datetime': get_subscription_dates(subscription),
        } for subscription in MeetingSubscription.query().fetch()
    ]
    for subscription in subscriptions:
        for user_preference in user_preferences:
            if subscription['id'] == user_preference['subscription_id']:
                for date in subscription['datetime']:
                    if date['id'] == user_preference['datetime_id']:
                        date['active'] = True

    return subscriptions


def get_subscription_dates(subscription):
    return [
        {
            'id': date.urlsafe(),
            'date': date.get().datetime.replace(tzinfo=utc).isoformat(),
            'active': False
        }
        for date in subscription.datetime
    ]


def get_specs_from_subscription(subscription):
    specs = []
    for subscription_datetime in subscription.datetime:

        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(
            hour=0, minute=0, second=0, microsecond=0)

        subscription_dt = subscription_datetime.get().datetime
        week_iter = week_start
        while week_iter.weekday() != subscription_dt.weekday():
            week_iter += timedelta(days=1)

        specs.append(
            MeetingSpec(
                meeting_subscription=subscription.key,
                datetime=week_iter.replace(
                    hour=subscription_dt.hour, minute=subscription_dt.minute)
            )
        )
    return week_start, specs


def store_specs_from_subscription(subscription_key, week_start, specs):
    """
    Idempotent function to store meeting specs for this week.
    """
    try:
        current_specs = MeetingSpec.query(
            MeetingSpec.meeting_subscription == subscription_key,
            MeetingSpec.datetime > week_start
        ).fetch()
    except NeedIndexError:
        current_specs = []

    if current_specs:
        return

    ndb.put_multi(specs)
    return specs
