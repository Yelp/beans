# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.logic.metrics import get_subscribers
from yelp_beans.models import MeetingSubscription


def test_get_subscribed_users(database, fake_user):
    subscribed_users = get_subscribers()
    assert len(subscribed_users) == 1
    assert subscribed_users[database.sub.key.urlsafe()] == ['darwin@yelp.com']


def test_get_subscribed_users_multiple(database, fake_user):
    subscription2 = MeetingSubscription(title='test1').put()
    subscribed_users = get_subscribers()

    assert len(subscribed_users) == 2
    assert subscribed_users[subscription2.urlsafe()] == []
    assert subscribed_users[database.sub.key.urlsafe()] == ['darwin@yelp.com']
