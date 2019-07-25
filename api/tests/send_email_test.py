# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.matching.match import generate_meetings
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.send_email import send_batch_initial_opt_in_email
from yelp_beans.send_email import send_batch_meeting_confirmation_email
from yelp_beans.send_email import send_batch_unmatched_email
from yelp_beans.send_email import send_batch_weekly_opt_in_email


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_weekly_opt_in_email(database, fake_user):
    for spec in get_specs_for_current_week():
        send_batch_weekly_opt_in_email(spec)


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_initial_opt_in_email(database, fake_user):
    send_batch_initial_opt_in_email([fake_user])


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_meeting_confirmation_email(database):
    pref = UserSubscriptionPreferences(subscription=database.sub.key, preference=database.prefs[0].key)
    pref.put()
    s3_url = 'https://s3-media2.fl.yelpcdn.com/assets/srv0/yelp_large_assets/'
    user_a = User(
        email='rkwills@yelp.com',
        photo_url=s3_url + 'a315bcce34b3/assets/img/illustrations/mascots/hammy.png',
        first_name='Hammy',
        last_name='Yelp',
        metadata={'department': 'Engineering'},
        subscription_preferences=[pref.key]
    )
    user_b = User(
        first_name='Darwin',
        last_name='Yelp',
        email='darwin@yelp.com',
        photo_url=s3_url + '36a31704362e/assets/img/illustrations/mascots/darwin.png',
        metadata={'department': 'Design'},
        subscription_preferences=[pref.key]
    )
    user_c = User(
        first_name='Carmin',
        last_name='Yelp',
        email='darwin@yelp.com',
        photo_url=s3_url + 'd71947670be7/assets/img/illustrations/mascots/carmen.png',
        metadata={'department': 'Design'},
        subscription_preferences=[pref.key]
    )
    user_a.put()
    user_b.put()
    user_c.put()
    matches = [tuple((user_a, user_b, user_c, pref))]
    send_batch_meeting_confirmation_email(matches, database.specs[0])


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_unmatched_email(database, fake_user):
    matches, unmatched = generate_meetings([fake_user], database.specs[0])
    send_batch_unmatched_email(unmatched)
