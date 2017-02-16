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

    MeetingSubscription(title='test1').put()

    with app.test_request_context('/v1/metrics'):
        response = metrics_api()
        assert response == json.dumps([{
            "meetings": 0,
            "subscribed": 0,
            "title": "test1",
        }])


def test_get_metrics_multiple(app, database, subscription, fake_user):
    with app.test_request_context('/v1/metrics'):
        response = metrics_api()
        assert response == json.dumps([{
            "meetings": 0,
            "subscribed": 1,
            "title": "Yelp Weekly",
        }])

    MeetingSubscription(title='test1').put()

    with app.test_request_context('/v1/metrics'):
        response = metrics_api()
        assert response == json.dumps([
            {"meetings": 0, "subscribed": 1, "title": "Yelp Weekly"},
            {"meetings": 0, "subscribed": 0, "title": "test1"}
        ])
