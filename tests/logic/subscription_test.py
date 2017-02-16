# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.logic.subscription import filter_subscriptions_by_user_data
from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import get_subscription_dates
from yelp_beans.logic.subscription import merge_subscriptions_with_preferences
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.models import MeetingSpec
from yelp_beans.models import Rule
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def test_get_specs_from_subscription(database):
    week_start, specs = get_specs_from_subscription(database.sub)
    assert len(specs) == 2


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
        'timezone': 'US/Pacific',
        'size': 2,
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


def test_filter_subscriptions_by_user_data(database):
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
    database.sub.rules = [rule]
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
