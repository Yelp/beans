import json
from datetime import datetime

import pytest
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.api.v1 import preferences
from yelp_beans.routes.api.v1.preferences import preferences_api
from yelp_beans.routes.api.v1.preferences import preferences_api_post
from yelp_beans.routes.api.v1.types import TimeSlot


def test_preferences_api_no_user(app, session):
    with app.test_request_context("/?email=darwin@yelp.com"):
        response = preferences_api()
    assert response.json == []


def test_preferences_api_user_exists(app, database, fake_user):
    with app.test_request_context("/?email=darwin@yelp.com"):
        response = preferences_api().json
    assert response == [
        {
            "id": database.sub.id,
            "title": "Yelp Weekly",
            "location": "8th Floor",
            "office": "USA: CA SF New Montgomery Office",
            "timezone": "America/Los_Angeles",
            "size": 2,
            "rule_logic": None,
            "datetime": [
                {"active": False, "date": "2017-01-20T19:00:00+00:00", "id": database.sub.datetime[1].id},
                {"active": True, "date": "2017-01-20T23:00:00+00:00", "id": database.sub.datetime[0].id, "auto_opt_in": True},
            ],
            "default_auto_opt_in": False,
        }
    ]


def test_preference_api_post(monkeypatch, app, database, fake_user):
    monkeypatch.setattr(preferences, "get_user", lambda x: fake_user)
    sub_key = database.sub.id
    assert fake_user.subscription_preferences != []
    with app.test_request_context(
        f"/v1/user/preferences/subscription/{sub_key}",
        method="POST",
        data=json.dumps(
            {
                database.sub.datetime[0].id: {"active": False},
                "email": fake_user.email,
            }
        ),
        content_type="application/json",
    ):
        response = preferences_api_post(sub_key)

    assert response == "OK"
    assert fake_user.subscription_preferences == []


def test_subscribe_api_post_no_user(client, session):
    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    subscription = MeetingSubscription(datetime=[sub_time])
    session.add(subscription)
    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={})
    assert resp.status_code == 400


def test_subscribe_api_post_user_cant_subscribe(client, session):
    user = User(first_name="tester", last_name="user", email="darwin@yelp.com", meta_data={"email": "darwin@yelp.com"})
    session.add(user)

    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    rule = Rule(name="email", value="not-darwin@yelp.com")
    subscription = MeetingSubscription(
        datetime=[sub_time],
        rule_logic="all",
        user_rules=[rule],
    )
    session.add(subscription)
    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email})
    assert resp.status_code == 403


def test_subscribe_api_post_user_has_existing(client, session):
    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=False,
    )
    session.add(subscription)

    # Setting auto_opt_in to true because subscription has default of false
    preference = UserSubscriptionPreferences(subscription=subscription, preference=sub_time, auto_opt_in=True)
    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[preference],
    )
    session.add(user)
    session.commit()

    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email})
    assert resp.status_code == 200
    assert resp.json == {
        "subscription": {
            "id": subscription.id,
            "default_auto_opt_in": False,
            "location": "test place",
            "name": "Test",
            "office": "tester",
            "rule_logic": None,
            "rules": [],
            "size": 2,
            # Keeping the first of the preferences
            "time_slots": [{"day": "thursday", "hour": 6, "minute": 0}],
            "timezone": "America/Los_Angeles",
        },
        "time_slot": {
            "day": "thursday",
            "hour": 6,
            "minute": 0,
        },
        "new_preference": False,
    }

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference == preference


@pytest.mark.parametrize("default_auto_opt_in", (True, False))
def test_subscribe_api_post_user_new_subscription(client, session, default_auto_opt_in):
    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=default_auto_opt_in,
    )
    session.add(subscription)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)
    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email})
    assert resp.status_code == 200
    assert resp.json == {
        "subscription": {
            "id": subscription.id,
            "default_auto_opt_in": default_auto_opt_in,
            "location": "test place",
            "name": "Test",
            "office": "tester",
            "rule_logic": None,
            "rules": [],
            "size": 2,
            # Keeping the first of the preferences
            "time_slots": [{"day": "thursday", "hour": 6, "minute": 0}],
            "timezone": "America/Los_Angeles",
        },
        "time_slot": {
            "day": "thursday",
            "hour": 6,
            "minute": 0,
        },
        "new_preference": True,
    }

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference.auto_opt_in == default_auto_opt_in
    assert new_preference.subscription == subscription
    assert new_preference.preference == sub_time


def test_subscribe_api_post_user_no_popular(client, session):
    sub_time_1 = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    sub_time_2 = SubscriptionDateTime(datetime=datetime(2017, 8, 20, 13, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time_1, sub_time_2],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=True,
    )
    session.add(subscription)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)
    session.commit()

    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email})
    assert resp.status_code == 200
    assert resp.json["time_slot"] == {
        "day": "thursday",
        "hour": 6,
        "minute": 0,
    }

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference.preference == sub_time_1


def test_subscribe_api_post_user_pick_popular(client, session):
    sub_time_1 = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    sub_time_2 = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 18, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time_1, sub_time_2],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=True,
    )
    session.add(subscription)
    # Make a fake preference, so second time slot is more popular
    preference = UserSubscriptionPreferences(subscription=subscription, preference=sub_time_2, auto_opt_in=True, user_id=200)
    session.add(preference)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)
    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email})
    assert resp.status_code == 200
    assert resp.json["time_slot"] == {
        "day": "thursday",
        "hour": 11,
        "minute": 0,
    }

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference.preference == sub_time_2


def test_subscribe_api_post_user_predefined_time(client, session):
    sub_time_1 = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    sub_time_2 = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 18, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time_1, sub_time_2],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=True,
    )
    session.add(subscription)
    # Make a fake preference, so second time slot is more popular
    preference = UserSubscriptionPreferences(subscription=subscription, preference=sub_time_2, auto_opt_in=True, user_id=200)
    session.add(preference)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)
    session.commit()
    time_slot = TimeSlot.from_sqlalchemy(sub_time_1, subscription.timezone)
    resp = client.post(
        f"/v1/user/preferences/subscribe/{subscription.id}",
        json={"email": user.email, "time_slot": time_slot.model_dump(mode="json")},
    )
    assert resp.status_code == 200
    assert resp.json["time_slot"] == {
        "day": time_slot.day.value,
        "hour": time_slot.hour,
        "minute": time_slot.minute,
    }

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference.preference == sub_time_1


@pytest.mark.parametrize("auto_opt_in", (True, False))
def test_subscribe_api_post_create_auto_opt_in_specified(client, session, auto_opt_in):
    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=True,
    )
    session.add(subscription)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)
    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email, "auto_opt_in": auto_opt_in})
    assert resp.status_code == 200

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()
    assert new_preference.auto_opt_in == auto_opt_in


@pytest.mark.parametrize("auto_opt_in", (True, False))
def test_subscribe_api_post_update_subscription(client, session, auto_opt_in):
    sub_time = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    subscription = MeetingSubscription(
        timezone="America/Los_Angeles",
        datetime=[sub_time],
        title="Test",
        size=2,
        office="tester",
        location="test place",
        user_rules=[],
        default_auto_opt_in=True,
    )
    session.add(subscription)

    user = User(
        first_name="tester",
        last_name="user",
        email="darwin@yelp.com",
        meta_data={"email": "darwin@yelp.com"},
        subscription_preferences=[],
    )
    session.add(user)

    preference_1 = UserSubscriptionPreferences(
        subscription=subscription, preference=sub_time, auto_opt_in=not auto_opt_in, user_id=user.id
    )
    session.add(preference_1)

    session.commit()
    resp = client.post(f"/v1/user/preferences/subscribe/{subscription.id}", json={"email": user.email, "auto_opt_in": auto_opt_in})
    assert resp.status_code == 200

    new_preference = session.query(UserSubscriptionPreferences).filter(UserSubscriptionPreferences.user_id == user.id).one()

    assert new_preference.auto_opt_in == auto_opt_in
