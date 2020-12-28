# -*- coding: utf-8 -*-
from yelp_beans.logic.metrics import get_subscribers
from yelp_beans.models import MeetingSubscription


def test_get_subscribed_users(database, fake_user):
    subscribed_users = get_subscribers()
    assert len(subscribed_users) == 1
    assert subscribed_users[database.sub.id] == ['darwin@yelp.com']


def test_get_subscribed_users_multiple(database, fake_user, session):
    subscription2 = MeetingSubscription(title='test1')
    session.add(subscription2)
    session.commit()
    subscribed_users = get_subscribers()

    assert len(subscribed_users) == 2
    assert subscribed_users[subscription2.id] == []
    assert subscribed_users[database.sub.id] == ['darwin@yelp.com']
