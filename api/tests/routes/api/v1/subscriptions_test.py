from datetime import datetime
from unittest import mock

import arrow
import pytest

from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime


@pytest.fixture
def mock_cur_time():

    def mock_return(timezone):
        return arrow.get("2017-08-01T12:00:00").to(timezone)

    with mock.patch('yelp_beans.routes.api.v1.subscriptions.arrow.now', side_effect=mock_return):
        yield


def test_create_subscription_minimal(client, session, mock_cur_time):
    resp = client.post('v1/subscriptions/', json={'name': 'test', 'time_slots': [{'day': 'monday', 'hour': 9}]})
    row = session.query(MeetingSubscription).filter(MeetingSubscription.id == resp.json['id']).one()

    assert row.title == 'test'
    assert row.size == 2
    assert row.location == 'Online'
    assert row.office == 'Remote'
    assert row.rule_logic is None
    assert row.timezone == 'America/Los_Angeles'
    assert row.user_rules == []

    assert len(row.datetime) == 1
    assert row.datetime[0].datetime.weekday() == 0
    assert row.datetime[0].datetime.hour == 16
    assert row.datetime[0].datetime.minute == 0


def test_create_subscription_full(client, session, mock_cur_time):
    resp = client.post(
        'v1/subscriptions/',
        json={
            'location': 'test site',
            'name': 'test',
            'office': 'test office',
            'rule_logic': 'all',
            'rules': [{'field': 'email', 'value': 'tester@yelp.test'}],
            'time_slots': [{'day': 'monday', 'hour': 9, 'minute': 5}],
            'timezone': 'America/New_York'
        },
    )
    row = session.query(MeetingSubscription).filter(MeetingSubscription.id == resp.json['id']).one()

    assert row.title == 'test'
    assert row.size == 2
    assert row.location == 'test site'
    assert row.office == 'test office'
    assert row.rule_logic == 'all'
    assert row.timezone == 'America/New_York'

    assert len(row.datetime) == 1
    assert row.datetime[0].datetime.weekday() == 0
    assert row.datetime[0].datetime.hour == 13
    assert row.datetime[0].datetime.minute == 5

    assert len(row.user_rules) == 1
    assert row.user_rules[0].name == 'email'
    assert row.user_rules[0].value == 'tester@yelp.test'


def test_get_subscriptions(client, session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    session.add(preference)
    subscription = MeetingSubscription(
        timezone='America/Los_Angeles',
        datetime=[preference],
        title="Test",
        size=2,
        office='tester',
        location='test place',
    )
    session.add(subscription)
    session.commit()

    resp = client.get('v1/subscriptions/')
    assert resp.json == [
        {
            'id': subscription.id,
            'location': 'test place',
            'name': "Test",
            'office': 'tester',
            'rule_logic': None,
            'rules': [],
            'size': 2,
            'time_slots': [{'day': 'thursday', 'hour': 6, 'minute': 0}],
            'timezone': 'America/Los_Angeles',
        },
    ]


def test_get_subscriptions_has_rule(client, session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    session.add(preference)
    rule = Rule(name='field', value='value')
    session.add(rule)
    subscription = MeetingSubscription(
        timezone='America/Los_Angeles',
        datetime=[preference],
        title="Test",
        size=2,
        office='tester',
        location='test place',
        rule_logic='all',
        user_rules=[rule],
    )
    session.add(subscription)
    session.commit()

    resp = client.get('v1/subscriptions/')
    assert resp.json == [
        {
            'id': subscription.id,
            'location': 'test place',
            'name': "Test",
            'office': 'tester',
            'rule_logic': 'all',
            'rules': [{'field': 'field', 'value': 'value'}],
            'size': 2,
            'time_slots': [{'day': 'thursday', 'hour': 6, 'minute': 0}],
            'timezone': 'America/Los_Angeles',
        },
    ]


def test_get_subscription(client, session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 7, 20, 13, 0))
    session.add(preference)
    rule = Rule(name='field', value='value')
    session.add(rule)
    subscription = MeetingSubscription(
        timezone='America/Los_Angeles',
        datetime=[preference],
        title="Test",
        size=2,
        office='tester',
        location='test place',
        rule_logic='all',
        user_rules=[rule],
    )
    session.add(subscription)
    session.commit()

    resp = client.get(f'v1/subscriptions/{subscription.id}')
    assert resp.json == {
        'id': subscription.id,
        'location': 'test place',
        'name': "Test",
        'office': 'tester',
        'rule_logic': 'all',
        'rules': [{'field': 'field', 'value': 'value'}],
        'size': 2,
        'time_slots': [{'day': 'thursday', 'hour': 6, 'minute': 0}],
        'timezone': 'America/Los_Angeles',
    }
