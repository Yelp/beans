# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
from collections import namedtuple
from datetime import datetime

import mock
import pytest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from pytz import timezone
from pytz import utc
from yelp_beans import send_email
from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


FAKE_USER = [{
    'first_name': 'Darwin',
    'last_name': 'Yelp',
    'email': 'darwin@yelp.com',
    'photo_url': (
        'https://s3-media4.fl.yelpcdn.com/assets/'
        'srv0/yelp_large_assets/3f74899c069c'
        '/assets/img/illustrations/mascots/darwin@2x.png'
    ),
    'department': 'Consumer',
    'business_title': 'Engineer',
}]


@pytest.yield_fixture(scope='session', autouse=True)
def mock_config():
    with open('tests/test_data/config.yaml') as config_file:
        data = config_file.read()
    with mock.patch(
        'yelp_beans.logic.config.open',
        mock.mock_open(read_data=data)
    ):
        yield


@pytest.yield_fixture(scope='session', autouse=True)
def sendgrid_mock():
    """This is active to prevent from sending a emails when testing"""
    with mock.patch.object(send_email, 'send_single_email'):
        yield


@pytest.fixture
def minimal_database():
    my_testbed = testbed.Testbed()
    my_testbed.activate()
    my_testbed.init_datastore_v3_stub()
    my_testbed.init_memcache_stub()
    # Clear ndb's in-context cache between tests.
    ndb.get_context().clear_cache()


@pytest.yield_fixture
def subscription():
    yield _subscription()


def _subscription():
    zone = 'America/Los_Angeles'
    preference_1 = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 23, 0, tzinfo=utc))
    # Easier to think/verify in Pacific time since we are based in SF
    assert preference_1.datetime.astimezone(timezone(zone)).hour == 15
    preference_1.datetime = preference_1.datetime.replace(tzinfo=None)
    preference_1.put()

    preference_2 = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 19, 0, tzinfo=utc))
    # Easier to think/verify in Pacific time since we are based in SF
    assert preference_2.datetime.astimezone(timezone(zone)).hour == 11
    preference_2.datetime = preference_2.datetime.replace(tzinfo=None)
    preference_2.put()

    rule = Rule(name='office', value='USA: CA SF New Montgomery Office').put()

    subscription = MeetingSubscription(
        title='Yelp Weekly',
        size=2,
        location='8th Floor',
        office='USA: CA SF New Montgomery Office',
        timezone=zone,
        datetime=[preference_1.key, preference_2.key],
        user_rules=[rule]
    )
    subscription.put()
    return subscription


@pytest.fixture
def database(minimal_database, subscription):
    MeetingInfo = namedtuple('MeetingInfo', ['sub', 'specs', 'prefs'])
    week_start, specs = get_specs_from_subscription(subscription)
    store_specs_from_subscription(subscription.key, week_start, specs)
    return MeetingInfo(
        subscription,
        specs,
        [
            subscription.datetime[0].get(),
            subscription.datetime[1].get()
        ]
    )


@pytest.fixture
def database_no_specs(minimal_database, subscription):
    MeetingInfo = namedtuple('MeetingInfo', ['sub', 'specs', 'prefs'])
    return MeetingInfo(
        subscription,
        [],
        [
            subscription.datetime[0].get(),
            subscription.datetime[1].get()
        ]
    )


@pytest.fixture
def employees():
    with open('tests/test_data/employees.json') as test_file:
        return test_file.read()


@pytest.yield_fixture
def data_source():
    yield [
        {
            'first_name': 'Sam',
            'last_name': 'Smith',
            'email': 'samsmith@yelp.com',
            'photo_url': 'www.cdn.com/SamSmith.png',
            'metadata': {
                'department': 'Engineering',
                'title': 'Engineer',
                'floor': '10',
                'desk': '100',
                'manager': 'Bo Demillo'
            }
        },
        {
            'first_name': 'Derrick',
            'last_name': 'Johnson',
            'email': 'derrickjohnson@yelp.com',
            'photo_url': 'www.cdn.com/DerrickJohnson.png',
            'metadata': {
                'department': 'Design',
                'title': 'Designer',
                'floor': '12',
                'desk': '102',
                'manager': 'Tracy Borne'
            }
        }
    ]


@pytest.yield_fixture
def data_source_by_key():
    yield {
        'samsmith@yelp.com': {
            'first_name': 'Sam',
            'last_name': 'Smith',
            'email': 'samsmith@yelp.com',
            'photo_url': 'www.cdn.com/SamSmith.png',
            'metadata': {
                'department': 'Engineering',
                'title': 'Engineer',
                'floor': '10',
                'desk': '100',
                'manager': 'Bo Demillo'
            }
        },
        'derrickjohnson@yelp.com': {
            'first_name': 'Derrick',
            'last_name': 'Johnson',
            'email': 'derrickjohnson@yelp.com',
            'photo_url': 'www.cdn.com/DerrickJohnson.png',
            'metadata': {
                'department': 'Design',
                'title': 'Designer',
                'floor': '12',
                'desk': '102',
                'manager': 'Derrick Johnson'
            }
        }
    }


@pytest.fixture
def app():
    from webapp import app
    app.testing = True
    return app


@pytest.fixture
def fake_user():
    yield _fake_user()


def _fake_user():
    user_list = []
    subscription = MeetingSubscription.query().get()
    for user in FAKE_USER:
        preferences = UserSubscriptionPreferences(
            preference=subscription.datetime[0],
            subscription=subscription.key,
        ).put()
        user_entity = User(
            first_name=user['first_name'],
            last_name=user['last_name'],
            email=user['email'],
            photo_url=user['photo_url'],
            metadata={
                'department': user['department'],
                'office': 'USA: CA SF New Montgomery Office',
                'company_profile_url': 'https://www.yelp.com/user_details?userid=nkN_do3fJ9xekchVC-v68A',
            },
            subscription_preferences=[preferences],
        )
        user_entity.put()
        user_list.append(user_entity)
    return user_list[0]


def create_dev_data():
    email = FAKE_USER[0]['email']
    user = User.query(User.email == email).get()
    if not user:
        _subscription()
        time.sleep(2)
        _fake_user()

        subscription = MeetingSubscription.query().get()
        week_start, specs = get_specs_from_subscription(subscription)
        store_specs_from_subscription(subscription.key, week_start, specs)
        logging.info('generated fake date for dev')
