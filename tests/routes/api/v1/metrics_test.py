# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.models import MeetingSubscription
from yelp_beans.routes.api.v1.metrics import metrics_api


def test_get_metrics(app, minimal_database):

    with app.test_request_context('/v1/metrics'):
        response = metrics_api()
        assert response == '[]'

    new_subscription = MeetingSubscription(title='test1')
    new_subscription.put()

    with app.test_request_context('/v1/metrics'):
        response = json.loads(metrics_api())
        assert response[0]["title"] == new_subscription.title
        assert response[0]["key"] == new_subscription.key.urlsafe()
        assert response[0]["week_participants"] == 0
        assert response[0]["subscribed"] == []


def test_get_metrics_multiple(app, database, subscription, fake_user):
    with app.test_request_context('/v1/metrics'):
        response = json.loads(metrics_api())
        assert len(response) == 1
        response = response[0]
        assert response['key'] == database.sub.key.urlsafe()
        assert response['subscribed'] == ['darwin@yelp.com']
        assert response['title'] == database.sub.title
        assert response['week_participants'] == 1

    new_subscription = MeetingSubscription(title='test1')
    new_subscription.put()

    with app.test_request_context('/v1/metrics'):
        response = json.loads(metrics_api())
        assert len(response) == 2

        assert response[0]['key'] == database.sub.key.urlsafe()
        assert response[0]['subscribed'] == [fake_user.email]
        assert response[0]['title'] == database.sub.title
        assert response[0]['week_participants'] == 1

        assert response[1]['key'] == new_subscription.key.urlsafe()
        assert response[1]['subscribed'] == []
        assert response[1]['title'] == new_subscription.title
        assert response[1]['week_participants'] == 0
