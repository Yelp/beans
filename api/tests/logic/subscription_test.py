# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

import pytest
from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.subscription import filter_subscriptions_by_user_data
from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import get_subscription_dates
from yelp_beans.logic.subscription import merge_subscriptions_with_preferences
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def test_get_specs_from_subscription(database):
    week_start, specs = get_specs_from_subscription(database.sub)
    assert len(specs) == 2

@pytest.mark.skip(reason="reverting timezone functionality")
def test_get_specs_from_subscription_pst(minimal_database):
    preference = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0)).put()
    subscription = MeetingSubscription(timezone='America/Los_Angeles', datetime=[preference]).put()
    _, specs = get_specs_from_subscription(subscription.get())
    assert len(specs) == 1
    assert get_meeting_datetime(specs[0]).hour == 13


@pytest.mark.skip(reason="reverting timezone functionality")
def test_get_specs_from_subscription_pdt(minimal_database):
    preference = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 13, 0)).put()
    subscription = MeetingSubscription(timezone='America/Los_Angeles', datetime=[preference]).put()
    _, specs = get_specs_from_subscription(subscription.get())
    assert get_meeting_datetime(specs[0]).hour == 13


def test_store_specs_from_subscription(database):
    week_start, specs = get_specs_from_subscription(database.sub)
    store_specs_from_subscription(database.sub.key, week_start, specs)
    assert len(MeetingSpec.query().fetch()) == 2


def test_get_subscription_dates(database):
    dates = get_subscription_dates(database.sub)
    assert len(dates) == 2
    assert dates[1]['date'] == '2017-01-20T19:00:00+00:00'


def test_merge_subscriptions_with_preferences(database, fake_user):
    merged_preferences = merge_subscriptions_with_preferences(fake_user)
    assert merged_preferences[0] == {
        'id': database.sub.key.urlsafe(),
        'title': 'Yelp Weekly',
        'location': '8th Floor',
        'office': 'USA: CA SF New Montgomery Office',
        'timezone': 'America/Los_Angeles',
        'size': 2,
        'rule_logic': None,
        'datetime': [
            {
                'active': True,
                'date': '2017-01-20T23:00:00+00:00',
                'id': database.sub.datetime[0].urlsafe()
            },
            {
                'active': False,
                'date': '2017-01-20T19:00:00+00:00',
                'id': database.sub.datetime[1].urlsafe()
            }
        ]
    }


def test_filter_subscriptions_by_user_data_any(database):
    preference = UserSubscriptionPreferences(
        subscription=database.sub.key,
        preference=database.prefs[0].key
    )
    preference.put()
    user = User(
        email='a@a.com',
        subscription_preferences=[preference.key]
    )
    user.metadata = {"department": "a"}
    user.put()

    rule = Rule(name="department", value="a").put()
    database.sub.user_rules = [rule]
    database.sub.rule_logic = 'any'
    database.sub.put()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]['id'] == database.sub.key.urlsafe()

    user.metadata = {"department": "b"}
    user.put()
    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert subscriptions == []


def test_filter_subscriptions_by_user_data_all(database):
    database.sub.rule_logic = 'all'
    rule1 = Rule(name="department", value="a").put()
    rule2 = Rule(name="location", value="c").put()
    database.sub.user_rules = [rule1, rule2]
    database.sub.put()

    preference = UserSubscriptionPreferences(
        subscription=database.sub.key,
        preference=database.prefs[0].key
    )
    preference.put()
    user = User(
        email='a@a.com',
        subscription_preferences=[preference.key]
    )
    user.metadata = {"department": "a", "location": "b"}
    user.put()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert subscriptions == []

    user.metadata = {'department': 'a', 'location': 'c'}
    user.put()
    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]['id'] == database.sub.key.urlsafe()


def test_filter_subscriptions_by_user_data_without_rules(database):
    database.sub.rule_logic = 'all'
    database.sub.user_rules = []
    database.sub.put()

    preference = UserSubscriptionPreferences(
        subscription=database.sub.key,
        preference=database.prefs[0].key
    )
    preference.put()
    user = User(
        email='a@a.com',
        subscription_preferences=[preference.key]
    )
    user.metadata = {"department": "a", "location": "b"}
    user.put()

    merged_preferences = merge_subscriptions_with_preferences(user)
    with pytest.raises(AssertionError):
        filter_subscriptions_by_user_data(merged_preferences, user)


def test_filter_subscriptions_by_user_data_none(database):
    database.sub.put()
    preference = UserSubscriptionPreferences(
        subscription=database.sub.key,
        preference=database.prefs[0].key,
    )
    preference.put()
    user = User(
        email='a@a.com',
        subscription_preferences=[preference.key]
    )
    user.put()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]['id'] == database.sub.key.urlsafe()


def test_filter_subscriptions_by_user_data_none_when_rules_exist(database):
    rule = Rule(name="department", value="b").put()
    database.sub.user_rules = [rule]
    database.sub.rule_logic = 'none'
    database.sub.put()
    preference = UserSubscriptionPreferences(
        subscription=database.sub.key,
        preference=database.prefs[0].key,
    )
    preference.put()
    user = User(
        email='a@a.com',
        subscription_preferences=[preference.key],
        metadata={'department': 'a'}
    )
    user.put()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]['id'] == database.sub.key.urlsafe()
