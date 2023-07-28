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
def test_get_specs_from_subscription_pst(session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    session.add(preference)
    subscription = MeetingSubscription(timezone="America/Los_Angeles", datetime=[preference])
    session.add(subscription)
    session.commit()
    _, specs = get_specs_from_subscription(subscription)
    assert len(specs) == 1
    assert get_meeting_datetime(specs[0]).hour == 13


@pytest.mark.skip(reason="reverting timezone functionality")
def test_get_specs_from_subscription_pdt(session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 13, 0))
    session.add(preference)
    subscription = MeetingSubscription(timezone="America/Los_Angeles", datetime=[preference])
    session.add(subscription)
    session.commit()
    _, specs = get_specs_from_subscription(subscription)
    assert get_meeting_datetime(specs[0]).hour == 13


def test_store_specs_from_subscription(database):
    week_start, specs = get_specs_from_subscription(database.sub)
    store_specs_from_subscription(database.sub, week_start, specs)
    assert len(MeetingSpec.query.all()) == 2


def test_get_subscription_dates(database):
    dates = get_subscription_dates(database.sub)
    assert len(dates) == 2
    # Dates are ordered so this is the reverse of how they were created
    assert dates[0]["date"] == "2017-01-20T19:00:00+00:00"


def test_merge_subscriptions_with_preferences(database, fake_user):
    merged_preferences = merge_subscriptions_with_preferences(fake_user)
    assert merged_preferences[0] == {
        "id": database.sub.id,
        "title": "Yelp Weekly",
        "location": "8th Floor",
        "office": "USA: CA SF New Montgomery Office",
        "timezone": "America/Los_Angeles",
        "size": 2,
        "rule_logic": None,
        "datetime": [
            {"active": False, "date": "2017-01-20T19:00:00+00:00", "id": database.sub.datetime[1].id},
            {"active": True, "date": "2017-01-20T23:00:00+00:00", "id": database.sub.datetime[0].id},
        ],
    }


def test_filter_subscriptions_by_user_data_any(database, session):
    preference = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference])
    user.meta_data = {"department": "a"}
    session.add(user)

    rule = Rule(name="department", value="a")
    session.add(rule)
    database.sub.user_rules = [rule]
    database.sub.rule_logic = "any"
    session.add(database.sub)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == database.sub.id

    user.meta_data = {"department": "b"}
    session.add(user)
    session.commit()
    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert subscriptions == []


def test_filter_subscriptions_by_user_data_list(database, session):
    preference = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference])
    user.meta_data = {"role": ["pushmaster", "technical_lead"]}
    session.add(user)

    rule = Rule(name="role", value="pushmaster")
    database.sub.user_rules = [rule]
    database.sub.rule_logic = "any"
    session.add(rule)
    session.add(database.sub)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == database.sub.id

    user.meta_data = {"role": "infra"}
    session.add(user)
    session.commit()
    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 0


def test_filter_subscriptions_by_user_data_all(database, session):
    database.sub.rule_logic = "all"
    rule1 = Rule(name="department", value="a")
    rule2 = Rule(name="location", value="c")
    database.sub.user_rules = [rule1, rule2]
    session.add(rule1)
    session.add(rule2)
    session.add(database.sub)

    preference = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference])
    user.meta_data = {"department": "a", "location": "b"}
    session.add(user)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert subscriptions == []

    user.meta_data = {"department": "a", "location": "c"}
    session.add(user)
    session.commit()
    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == database.sub.id


def test_filter_subscriptions_by_user_data_without_rules(database, session):
    database.sub.rule_logic = "all"
    database.sub.user_rules = []
    session.add(database.sub)

    preference = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference])
    user.meta_data = {"department": "a", "location": "b"}
    session.add(user)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    with pytest.raises(AssertionError):
        filter_subscriptions_by_user_data(merged_preferences, user)


def test_filter_subscriptions_by_user_data_none(database, session):
    session.add(database.sub)
    preference = UserSubscriptionPreferences(
        subscription=database.sub,
        preference=database.prefs[0],
    )
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference])
    session.add(user)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == database.sub.id


def test_filter_subscriptions_by_user_data_none_when_rules_exist(database, session):
    rule = Rule(name="department", value="b")
    session.add(rule)
    database.sub.user_rules = [rule]
    database.sub.rule_logic = "none"
    session.add(database.sub)
    preference = UserSubscriptionPreferences(
        subscription=database.sub,
        preference=database.prefs[0],
    )
    session.add(preference)
    user = User(email="a@a.com", subscription_preferences=[preference], meta_data={"department": "a"})
    session.add(user)
    session.commit()

    merged_preferences = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(merged_preferences, user)

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == database.sub.id
